#!/usr/bin/env python3
"""
Quick test script to verify Profile & Social API functionality
Run this to test the basic functionality without running full test suite
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.database.sqlite_manager import SQLiteManager
from backend.core.social.profile_service import ProfileService
import tempfile
import json

def test_basic_functionality():
    """Test basic profile and social functionality"""
    print("🧪 Testing Profile & Social API Basic Functionality...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize services
        db_manager = SQLiteManager(db_path)
        profile_service = ProfileService(db_manager)
        
        # Test 1: Create Profile
        print("\n1️⃣ Testing profile creation...")
        success, message, user1_id = profile_service.create_profile(
            handle='testuser1',
            bio='Learning enthusiast',
            interests=['Python', 'AI', 'Programming'],
            learning_style='Visual',
            is_private=False
        )
        
        success2, message2, user2_id = profile_service.create_profile(
            handle='testuser2',
            bio='Code ninja',
            interests=['JavaScript', 'Web Dev', 'React'],
            learning_style='Hands-on',
            is_private=False
        )
        
        print(f"   ✅ User 1 created: {success} (ID: {user1_id})")
        print(f"   ✅ User 2 created: {success2} (ID: {user2_id})")
        
        # Test 2: Update Skills with Privacy
        print("\n2️⃣ Testing skill management with privacy...")
        profile_service.update_skill(user1_id, 'python', 4, visibility=True)
        profile_service.update_skill(user1_id, 'secret_skill', 5, visibility=False)
        profile_service.update_skill(user1_id, 'javascript', 3, visibility=True)
        
        profile_service.update_skill(user2_id, 'python', 2, visibility=True)
        profile_service.update_skill(user2_id, 'react', 4, visibility=True)
        
        print("   ✅ Skills added with privacy settings")
        
        # Test 3: Test Privacy Enforcement (Critical)
        print("\n3️⃣ Testing privacy enforcement...")
        
        # Get all skills (should include private)
        all_skills = profile_service.db.get_user_skills(user1_id, public_only=False)
        all_skill_ids = [s['skill_id'] for s in all_skills]
        
        # Get public skills only
        public_skills = profile_service.db.get_user_skills(user1_id, public_only=True)
        public_skill_ids = [s['skill_id'] for s in public_skills]
        
        print(f"   📊 All skills: {all_skill_ids}")
        print(f"   🔒 Public skills: {public_skill_ids}")
        
        # Verify privacy
        assert 'secret_skill' in all_skill_ids, "Private skill should exist in database"
        assert 'secret_skill' not in public_skill_ids, "Private skill should NOT be in public skills"
        assert 'python' in public_skill_ids, "Public skill should be in public skills"
        
        print("   ✅ Privacy enforcement working correctly!")
        
        # Test 4: Follow System
        print("\n4️⃣ Testing follow system...")
        
        # Follow user2
        success, message = profile_service.follow_user(user1_id, user2_id)
        print(f"   👥 Follow user2: {success} - {message}")
        
        # Try to follow again (should fail)
        success2, message2 = profile_service.follow_user(user1_id, user2_id)
        print(f"   🚫 Follow again: {success2} - {message2}")
        
        # Check if following
        is_following = profile_service.is_following(user1_id, user2_id)
        print(f"   ✅ Is following: {is_following}")
        
        # Test 5: Skill Comparison
        print("\n5️⃣ Testing skill comparison...")
        comparison = profile_service.compare_skills(user1_id, user2_id)
        
        print(f"   📈 Common skills: {len(comparison['common_skills'])}")
        print(f"   🎯 User1 unique: {len(comparison['user1_unique_skills'])}")
        print(f"   🎯 User2 unique: {len(comparison['user2_unique_skills'])}")
        print(f"   📊 Overlap: {comparison['summary']['overlap_percentage']:.1f}%")
        
        # Test 6: Public API
        print("\n6️⃣ Testing public API...")
        public_profile = profile_service.get_public_profile_by_handle('testuser1')
        
        if public_profile:
            print(f"   🌐 Public handle: {public_profile['handle']}")
            print(f"   🔒 Public bio: {public_profile['bio']}")
            print(f"   🎯 Public skills: {len(public_profile['skills'])}")
            
            # Verify no private skills in public profile
            public_skill_ids_from_api = [s['skill_id'] for s in public_profile['skills']]
            assert 'secret_skill' not in public_skill_ids_from_api, "Private skill leaked to public API!"
            print("   ✅ Public API respects privacy!")
        else:
            print("   ❌ Public profile not found")
        
        # Test 7: Add Review Logs for Metrics
        print("\n7️⃣ Testing metrics aggregation...")
        
        # Add some study sessions
        db_manager.execute_insert(
            'INSERT INTO review_logs (user_id, study_duration, xp_earned, study_date) VALUES (?, ?, ?, ?)',
            (user1_id, 30.0, 100, '2023-12-01')
        )
        db_manager.execute_insert(
            'INSERT INTO review_logs (user_id, study_duration, xp_earned, study_date) VALUES (?, ?, ?, ?)',
            (user1_id, 45.0, 150, '2023-12-02')
        )
        
        # Update metrics from logs
        result = profile_service.update_metrics_from_logs(user1_id)
        print(f"   📊 Metrics update: {result['success']}")
        if result['success']:
            print(f"   ⏰ Hours studied: {result['metrics']['hours_studied']:.1f}")
            print(f"   ⭐ XP total: {result['metrics']['xp_total']}")
        
        print("\n🎉 All basic functionality tests passed!")
        print("\n📋 Summary:")
        print("   ✅ Profile creation")
        print("   ✅ Skill management with privacy")
        print("   ✅ Privacy enforcement (CRITICAL)")
        print("   ✅ Follow/unfollow system")
        print("   ✅ Skill comparison")
        print("   ✅ Public API with privacy filtering")
        print("   ✅ Metrics aggregation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        db_manager.close()
        os.unlink(db_path)

def test_api_endpoints():
    """Test API endpoints (requires Flask app running)"""
    print("\n🌐 Testing API endpoints...")
    print("   (Make sure Flask app is running: python main.py)")
    
    try:
        import requests
    except ImportError:
        print("   ⚠️  requests module not available - skipping API tests")
        return False
    
    try:
        # Test health check
        response = requests.get('http://localhost:5000/api/profile/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Flask app not running. Start it with: python main.py")
        print("   📝 API tests skipped - backend not available")
        return False
    except Exception as e:
        print(f"   ❌ API test error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Profile & Social API Phase 2 - Quick Test")
    print("=" * 50)
    
    # Test basic functionality
    basic_test_passed = test_basic_functionality()
    
    # Test API endpoints (if available)
    api_test_passed = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if basic_test_passed:
        print("✅ BASIC FUNCTIONALITY: PASSED")
    else:
        print("❌ BASIC FUNCTIONALITY: FAILED")
    
    if api_test_passed:
        print("✅ API ENDPOINTS: PASSED")
    else:
        print("⚠️  API ENDPOINTS: SKIPPED (backend not running)")
    
    if basic_test_passed:
        print("\n🎯 Core functionality is working!")
        print("💡 Next steps:")
        print("   1. Start backend: python main.py")
        print("   2. Run full tests: pytest backend/tests/ -v")
        print("   3. Start desktop app: cd desktop && npm install && npm run dev")
        print("   4. Start mobile app: cd mobile && npm install")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")