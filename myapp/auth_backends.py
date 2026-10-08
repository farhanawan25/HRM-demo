from myapp.models import Users

class CustomUserWrapper:
    def __init__(self, user_obj):
        self.user_obj = user_obj
        self.id = user_obj.USER_ID
        self.username = user_obj.USER_ID
        self.is_authenticated = True
        self.is_active = True
        self.is_staff = True  # Required for admin access
        self.is_superuser = True  # Full permissions

    def __getattr__(self, attr):
        return getattr(self.user_obj, attr)

    def save(self, *args, **kwargs):
        # Skip saving since the real model doesn't support last_login
        pass
        
    # Add these methods required by Django admin
    def has_module_perms(self, app_label):
        return True  # Allow access to all apps
        
    def has_perm(self, perm, obj=None):
        return True  # Allow all permissions
        
    def get_all_permissions(self, obj=None):
        return set()  # Return an empty set or specific permissions if needed

class CustomUserBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            # Check if this is an admin login attempt
            is_admin_login = request and request.path and request.path.startswith('/admin/')
            
            # Check if user exists with given credentials
            user = Users.objects.get(USER_ID=username, USER_PSWD=password)
            
            # If it's an admin login, you might want to add additional checks here
            # For example, check if user has a specific role or attribute
            # if is_admin_login and not user.is_admin:  # Replace with your actual admin check
            #     return None
            
            # Return the wrapped user
            return CustomUserWrapper(user)
        except Users.DoesNotExist:
            return None
        except Exception as e:
            # Log the error for debugging
            print(f"Authentication error: {str(e)}")
            return None

    def get_user(self, user_id):
        try:
            user = Users.objects.get(USER_ID=user_id)
            return CustomUserWrapper(user)
        except Users.DoesNotExist:
            return None