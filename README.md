UPDATE users
SET password_changed_at = NOW()
WHERE email = 'ashmita@todo.com'
