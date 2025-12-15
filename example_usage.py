#!/usr/bin/env python3
"""
Example usage of the Profile Social API

This script demonstrates how to use the profile service and database manager.
"""

from backend.database.sqlite_manager import SQLiteManager
from backend.core.social.profile_service import ProfileService


def main():
    print("=== Profile Social API Demo ===\n")
    
    db = SQLiteManager("demo.db")
    service = ProfileService(db)
    
    print("1. Creating users...")
    alice = service.create_or_get_user("alice", "public")
    bob = service.create_or_get_user("bob", "public")
    charlie = service.create_or_get_user("charlie", "private")
    print(f"   Created: @{alice['handle']}, @{bob['handle']}, @{charlie['handle']}\n")
    
    print("2. Setting up Alice's profile...")
    service.upsert_profile(
        alice['id'],
        bio="Software engineer and lifelong learner",
        interests="python,machine learning,web development",
        learning_style="visual"
    )
    print("   Profile created\n")
    
    print("3. Adding skills for Alice...")
    service.update_skills(alice['id'], [
        {"skill_id": "python", "skill_name": "Python", "mastery": 0.85, "visibility": "public"},
        {"skill_id": "javascript", "skill_name": "JavaScript", "mastery": 0.75, "visibility": "public"},
        {"skill_id": "secret-tech", "skill_name": "Secret Technology", "mastery": 0.95, "visibility": "private"}
    ])
    print("   Skills added (2 public, 1 private)\n")
    
    print("4. Adding study logs for Alice...")
    db.add_review_log(alice['id'], 60)
    db.add_review_log(alice['id'], 90)
    db.add_review_log(alice['id'], 45)
    print("   Logged 3 study sessions\n")
    
    print("5. Aggregating metrics...")
    metrics = service.aggregate_metrics(alice['id'])
    print(f"   Hours studied: {metrics['hours_studied']}")
    print(f"   XP total: {metrics['xp_total']}")
    print(f"   Streak: {metrics['streak_days']} days\n")
    
    print("6. Setting up Bob's profile...")
    service.upsert_profile(
        bob['id'],
        bio="Data scientist exploring AI",
        interests="machine learning,statistics,python"
    )
    service.update_skills(bob['id'], [
        {"skill_id": "python", "skill_name": "Python", "mastery": 0.70, "visibility": "public"},
        {"skill_id": "r-lang", "skill_name": "R Programming", "mastery": 0.80, "visibility": "public"}
    ])
    print("   Bob's profile created\n")
    
    print("7. Alice follows Bob...")
    result = service.follow_user(alice['id'], "bob")
    print(f"   Success: {result['success']}\n")
    
    print("8. Comparing Alice and Bob's skills...")
    comparison = service.compare_skills(alice['id'], bob['id'])
    print(f"   Common skills: {len(comparison['common_skills'])}")
    for skill in comparison['common_skills']:
        print(f"      - {skill['skill_name']}: Alice {skill['user1_mastery']:.0%}, Bob {skill['user2_mastery']:.0%}")
    print(f"   Alice's unique: {len(comparison['user1_unique_skills'])}")
    print(f"   Bob's unique: {len(comparison['user2_unique_skills'])}\n")
    
    print("9. Getting Alice's public profile...")
    public_profile = service.get_public_profile("alice")
    print(f"   Handle: @{public_profile['handle']}")
    print(f"   Bio: {public_profile.get('bio', 'N/A')}")
    print(f"   Public skills: {len(public_profile['skills'])}")
    for skill in public_profile['skills']:
        print(f"      - {skill['skill_name']}: {skill['mastery']:.0%}")
    print(f"   Note: Private skill 'Secret Technology' is hidden\n")
    
    print("10. Updating privacy settings...")
    service.update_privacy_settings(alice['id'], privacy_bio=1)
    public_profile = service.get_public_profile("alice")
    print(f"   Bio now private: {'bio' not in public_profile}\n")
    
    print("11. Getting full profile (authenticated)...")
    full_profile = service.get_full_profile(alice['id'])
    print(f"   Total skills (including private): {len(full_profile['skills'])}")
    print(f"   Followers: {full_profile['follower_count']}")
    print(f"   Following: {full_profile['following_count']}\n")
    
    print("=== Demo Complete ===")
    print("\nDatabase file created: demo.db")
    print("You can inspect it with: sqlite3 demo.db")


if __name__ == "__main__":
    main()
