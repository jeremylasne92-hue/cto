export interface User {
  id: number;
  handle: string;
  visibility_default: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  user_id: number;
  bio?: string;
  interests?: string;
  learning_style?: string;
  privacy_bio: number;
  privacy_interests: number;
  privacy_learning_style: number;
  created_at: string;
  updated_at: string;
}

export interface UserMetrics {
  user_id: number;
  hours_studied: number;
  xp_total: number;
  streak_days: number;
  certifications: string[];
  updated_at: string;
}

export interface UserSkill {
  id: number;
  user_id: number;
  skill_id: string;
  skill_name: string;
  mastery: number;
  visibility: string;
  created_at: string;
  updated_at: string;
}

export interface FullProfile {
  user: User;
  profile: UserProfile;
  metrics: UserMetrics;
  skills: UserSkill[];
  followers: User[];
  following: User[];
  follower_count: number;
  following_count: number;
}

export interface PublicProfile {
  handle: string;
  visibility_default: string;
  bio?: string;
  interests?: string;
  learning_style?: string;
  skills: UserSkill[];
  metrics?: {
    hours_studied: number;
    xp_total: number;
    streak_days: number;
    certifications: string[];
  };
  follower_count: number;
}

export interface SkillComparison {
  skill_id: string;
  skill_name: string;
  user1_mastery: number;
  user2_mastery: number;
  difference: number;
}

export interface ComparisonResult {
  user1: { id: number; handle: string };
  user2: { id: number; handle: string };
  common_skills: SkillComparison[];
  user1_unique_skills: UserSkill[];
  user2_unique_skills: UserSkill[];
}
