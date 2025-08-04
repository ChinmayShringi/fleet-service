"""
User Service
Handles user authentication and management using Excel file as database
"""

import os
import pandas as pd
import hashlib
from datetime import datetime
from constants.file_constants import USER_DATA, ensure_database_directory

class UserService:
    
    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(plain_password, hashed_password):
        """Verify password against hash"""
        return UserService._hash_password(plain_password) == hashed_password
    
    @staticmethod
    def _ensure_user_file():
        """Create user.xlsx file if it doesn't exist"""
        ensure_database_directory()
        
        if not os.path.exists(USER_DATA):
            # Create new user file with proper columns
            df = pd.DataFrame(columns=[
                'id',
                'username', 
                'email',
                'password_hash',
                'full_name',
                'role',
                'created_at',
                'last_login',
                'is_active'
            ])
            df.to_excel(USER_DATA, index=False)
            print(f"Created new user database: {USER_DATA}")
    
    @staticmethod
    def get_all_users():
        """Get all users (without passwords)"""
        try:
            UserService._ensure_user_file()
            df = pd.read_excel(USER_DATA)
            
            # Remove password column for security
            if 'password_hash' in df.columns:
                df = df.drop(columns=['password_hash'])
            
            return {
                'success': True,
                'users': df.to_dict('records'),
                'count': len(df)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get users: {str(e)}'
            }
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        try:
            UserService._ensure_user_file()
            df = pd.read_excel(USER_DATA)
            
            user_data = df[df['username'] == username]
            if user_data.empty:
                return None
            
            return user_data.iloc[0].to_dict()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        try:
            UserService._ensure_user_file()
            df = pd.read_excel(USER_DATA)
            
            user_data = df[df['email'] == email]
            if user_data.empty:
                return None
            
            return user_data.iloc[0].to_dict()
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def register_user(username, email, password, full_name=None, role='user'):
        """Register a new user"""
        try:
            UserService._ensure_user_file()
            
            # Check if username already exists
            if UserService.get_user_by_username(username):
                return {
                    'success': False,
                    'message': 'Username already exists'
                }
            
            # Check if email already exists
            if UserService.get_user_by_email(email):
                return {
                    'success': False,
                    'message': 'Email already exists'
                }
            
            # Read existing users
            df = pd.read_excel(USER_DATA)
            
            # Generate new user ID
            new_id = 1 if df.empty else int(df['id'].max()) + 1
            
            # Create new user record
            new_user = {
                'id': new_id,
                'username': username,
                'email': email,
                'password_hash': UserService._hash_password(password),
                'full_name': full_name or username,
                'role': role,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': None,
                'is_active': True
            }
            
            # Add new user to dataframe
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(USER_DATA, index=False)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': new_id,
                    'username': username,
                    'email': email,
                    'full_name': full_name or username,
                    'role': role
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
    
    @staticmethod
    def login_user(username_or_email, password):
        """Login user with username or email"""
        try:
            # Try to get user by username first, then by email
            user = UserService.get_user_by_username(username_or_email)
            if not user:
                user = UserService.get_user_by_email(username_or_email)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid credentials'
                }
            
            # Check if user is active
            if not user.get('is_active', True):
                return {
                    'success': False,
                    'message': 'Account is disabled'
                }
            
            # Verify password
            if not UserService._verify_password(password, user['password_hash']):
                return {
                    'success': False,
                    'message': 'Invalid credentials'
                }
            
            # Update last login using username
            UserService._update_last_login(user['username'])
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role']
                },
                'token': f"mock_token_{user['id']}_{user['username']}"  # Simple token for now
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }
    
    @staticmethod
    def _update_last_login(username):
        """Update user's last login timestamp"""
        try:
            df = pd.read_excel(USER_DATA)
            df.loc[df['username'] == username, 'last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_excel(USER_DATA, index=False)
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        try:
            UserService._ensure_user_file()
            df = pd.read_excel(USER_DATA)
            
            total_users = len(df)
            active_users = len(df[df['is_active'] == True]) if 'is_active' in df.columns else total_users
            
            return {
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get stats: {str(e)}'
            }
    
    @staticmethod
    def create_default_admin():
        """Create default admin user if it doesn't exist"""
        try:
            UserService._ensure_user_file()
            
            # Check if admin user already exists
            existing_admin = UserService.get_user_by_email('admin@gmail.com')
            if existing_admin:
                print("Default admin user already exists")
                return {
                    'success': True,
                    'message': 'Default admin user already exists'
                }
            
            # Create default admin user
            result = UserService.register_user(
                username='admin',
                email='admin@gmail.com',
                password='admin',
                full_name='System Administrator',
                role='admin'
            )
            
            if result['success']:
                print("Default admin user created successfully")
                print("Email: admin@gmail.com")
                print("Password: admin")
                return result
            else:
                print(f"Failed to create default admin user: {result['message']}")
                return result
                
        except Exception as e:
            error_msg = f'Failed to create default admin user: {str(e)}'
            print(error_msg)
            return {
                'success': False,
                'message': error_msg
            }