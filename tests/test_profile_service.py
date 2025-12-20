import unittest
import os
import tempfile
from backend.database.sqlite_manager import SQLiteManager
from backend.core.social.profile_service import ProfileService


class TestProfileService(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = SQLiteManager(self.db_path)
        self.service = ProfileService(self.db)
        
        self.user1_id = self.db.create_user('testuser1', 'public')
        self.user2_id = self.db.create_user('testuser2', 'public')
        self.user3_id = self.db.create_user('privateuser', 'private')

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_or_get_user(self):
        user = self.service.create_or_get_user('newuser')
        self.assertIsNotNone(user)
        self.assertEqual(user['handle'], 'newuser')
        
        same_user = self.service.create_or_get_user('newuser')
        self.assertEqual(user['id'], same_user['id'])

    def test_upsert_profile(self):
        profile = self.service.upsert_profile(
            self.user1_id,
            bio='Test bio',
            interests='python,machine learning',
            learning_style='visual'
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['profile']['bio'], 'Test bio')
        self.assertEqual(profile['profile']['interests'], 'python,machine learning')

    def test_update_privacy_settings(self):
        self.service.upsert_profile(
            self.user1_id,
            bio='Private bio'
        )
        
        profile = self.service.update_privacy_settings(
            self.user1_id,
            privacy_bio=1
        )
        
        self.assertEqual(profile['profile']['privacy_bio'], 1)

    def test_update_skills(self):
        skills = [
            {
                'skill_id': 'python',
                'skill_name': 'Python',
                'mastery': 0.8,
                'visibility': 'public'
            },
            {
                'skill_id': 'javascript',
                'skill_name': 'JavaScript',
                'mastery': 0.6,
                'visibility': 'private'
            }
        ]
        
        result = self.service.update_skills(self.user1_id, skills)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['skill_name'], 'Python')

    def test_aggregate_metrics(self):
        self.db.add_review_log(self.user1_id, 60)
        self.db.add_review_log(self.user1_id, 90)
        
        metrics = self.service.aggregate_metrics(self.user1_id)
        
        self.assertEqual(metrics['hours_studied'], 2.5)
        self.assertEqual(metrics['xp_total'], 0)
        self.assertEqual(metrics['streak_days'], 0)

    def test_get_public_profile_respects_privacy(self):
        self.service.upsert_profile(
            self.user1_id,
            bio='Public bio',
            interests='coding,reading',
            learning_style='visual'
        )
        
        self.service.update_privacy_settings(
            self.user1_id,
            privacy_bio=0,
            privacy_interests=1,
            privacy_learning_style=0
        )
        
        self.service.update_skills(self.user1_id, [
            {
                'skill_id': 'python',
                'skill_name': 'Python',
                'mastery': 0.8,
                'visibility': 'public'
            },
            {
                'skill_id': 'secret',
                'skill_name': 'Secret Skill',
                'mastery': 0.9,
                'visibility': 'private'
            }
        ])
        
        public_profile = self.service.get_public_profile('testuser1')
        
        self.assertIsNotNone(public_profile)
        self.assertEqual(public_profile['bio'], 'Public bio')
        self.assertNotIn('interests', public_profile)
        self.assertEqual(public_profile['learning_style'], 'visual')
        
        self.assertEqual(len(public_profile['skills']), 1)
        self.assertEqual(public_profile['skills'][0]['skill_name'], 'Python')

    def test_private_skill_not_leaked(self):
        self.service.update_skills(self.user1_id, [
            {
                'skill_id': 'private-skill',
                'skill_name': 'Private Skill',
                'mastery': 0.9,
                'visibility': 'private'
            }
        ])
        
        public_profile = self.service.get_public_profile('testuser1')
        self.assertEqual(len(public_profile['skills']), 0)

    def test_follow_lifecycle(self):
        result = self.service.follow_user(self.user1_id, 'testuser2')
        self.assertTrue(result['success'])
        
        is_following = self.service.is_following(self.user1_id, self.user2_id)
        self.assertTrue(is_following)
        
        duplicate_result = self.service.follow_user(self.user1_id, 'testuser2')
        self.assertFalse(duplicate_result['success'])
        
        unfollow_result = self.service.unfollow_user(self.user1_id, 'testuser2')
        self.assertTrue(unfollow_result['success'])
        
        is_following = self.service.is_following(self.user1_id, self.user2_id)
        self.assertFalse(is_following)

    def test_cannot_follow_self(self):
        result = self.service.follow_user(self.user1_id, 'testuser1')
        self.assertFalse(result['success'])
        self.assertIn('yourself', result['error'])

    def test_follow_nonexistent_user(self):
        result = self.service.follow_user(self.user1_id, 'nonexistent')
        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'])

    def test_compare_skills(self):
        self.service.update_skills(self.user1_id, [
            {'skill_id': 'python', 'skill_name': 'Python', 'mastery': 0.8, 'visibility': 'public'},
            {'skill_id': 'react', 'skill_name': 'React', 'mastery': 0.6, 'visibility': 'public'}
        ])
        
        self.service.update_skills(self.user2_id, [
            {'skill_id': 'python', 'skill_name': 'Python', 'mastery': 0.5, 'visibility': 'public'},
            {'skill_id': 'node', 'skill_name': 'Node.js', 'mastery': 0.7, 'visibility': 'public'}
        ])
        
        comparison = self.service.compare_skills(self.user1_id, self.user2_id)
        
        self.assertEqual(len(comparison['common_skills']), 1)
        self.assertEqual(comparison['common_skills'][0]['skill_id'], 'python')
        self.assertAlmostEqual(comparison['common_skills'][0]['difference'], 0.3, places=5)
        
        self.assertEqual(len(comparison['user1_unique_skills']), 1)
        self.assertEqual(comparison['user1_unique_skills'][0]['skill_id'], 'react')
        
        self.assertEqual(len(comparison['user2_unique_skills']), 1)
        self.assertEqual(comparison['user2_unique_skills'][0]['skill_id'], 'node')

    def test_get_full_profile(self):
        self.service.upsert_profile(self.user1_id, bio='Test bio')
        self.service.update_skills(self.user1_id, [
            {'skill_id': 'python', 'skill_name': 'Python', 'mastery': 0.8, 'visibility': 'public'}
        ])
        self.db.add_review_log(self.user1_id, 120)
        
        profile = self.service.get_full_profile(self.user1_id)
        
        self.assertIsNotNone(profile)
        self.assertIn('user', profile)
        self.assertIn('profile', profile)
        self.assertIn('skills', profile)
        self.assertIn('followers', profile)
        self.assertIn('following', profile)


if __name__ == '__main__':
    unittest.main()
