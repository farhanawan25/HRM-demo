# Updated middleware.py for custom database user table

from django.shortcuts import redirect
from django.urls import resolve
from django.http import JsonResponse
from django.contrib import messages
from django.db import connection
from .models import ViewsAccess, UserViewPermission
import logging

logger = logging.getLogger(__name__)

class ViewPermissionMiddleware:
    """
    Middleware to control access to views based on user permissions
    Works with custom database USERS table
    """
    
    # Views that should be excluded from permission checking
    EXCLUDED_VIEWS = [
        'no_access',
        'login',
        'logout',
        'admin:index',
        'static',
        'media',
        # Admin-only views (these have their own protection)
        'system_access_control',
        'manage_views',
        'get_user_permissions',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def is_database_admin(self, user):
        """Check if user is admin from database USERS table"""
        if not user.is_authenticated:
            return False
        
        try:
            with connection.cursor() as cursor:
                # Adjust this query based on your USERS table structure
                cursor.execute("""
                    SELECT USER_TYPE, IS_ADMIN, USER_ROLE 
                    FROM USERS 
                    WHERE USER_ID = %s
                """, [user.id])
                
                result = cursor.fetchone()
                if result:
                    # Check USER_TYPE field
                    if result[0] and result[0].upper() == 'ADMIN':
                        return True
                    
                    # Check IS_ADMIN field (if you have this column)
                    if len(result) > 1 and result[1]:
                        return True
                    
                    # Check USER_ROLE field
                    if len(result) > 2 and result[2] and result[2].upper() in ['ADMIN', 'ADMINISTRATOR']:
                        return True
                        
        except Exception as e:
            #logger.error(f"Error checking database admin status: {e}")
            return False
        
        return False

    def process_request(self, request):
        # Skip middleware for unauthenticated users
        if not request.user.is_authenticated:
            return None
            
        try:
            # Get the view name from URL
            resolver_match = resolve(request.path_info)
            view_name = resolver_match.url_name
            
            # Skip if no view name or in excluded views
            if not view_name or any(excluded in view_name for excluded in self.EXCLUDED_VIEWS):
                return None
            
            # Skip for database admins (they have access to everything)
            if self.is_database_admin(request.user):
                return None
                
            # Check if view requires permission
            try:
                view_obj = ViewsAccess.objects.get(view_name=view_name, is_active=True)
                
                # Check if user has permission
                has_permission = UserViewPermission.objects.filter(
                    user_id=request.user.id, 
                    view=view_obj
                ).exists()
                
                if not has_permission:
                    logger.warning(f"Access denied for user {request.user.id} to view {view_name}")
                    
                    # Handle AJAX requests differently
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'error': 'Access denied',
                            'message': 'You do not have permission to access this resource.'
                        }, status=403)
                    
                    messages.error(request, f"You don't have permission to access '{view_obj.view_desc or view_name}'")
                    return redirect('no_access')
                    
            except ViewsAccess.DoesNotExist:
                # View not in access control system, allow access
                pass
                
        except Exception as e:
            logger.error(f"Error in ViewPermissionMiddleware: {str(e)}")
            # On error, allow access to prevent system lockout
            pass
            
        return None