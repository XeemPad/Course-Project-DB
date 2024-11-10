SELECT
    idIntUser,
    login,
    user_group
FROM InternalUser
WHERE 1=1
    AND login='$login'
    AND password='$password'