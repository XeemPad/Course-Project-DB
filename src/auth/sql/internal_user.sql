SELECT
    idIntUser,
    login,
    user_group,
    idWaiter
FROM InternalUser
WHERE 1=1
    AND login='$login'
    AND password='$password'