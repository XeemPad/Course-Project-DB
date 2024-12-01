SELECT
    idIntUser,
    login,
    user_group,
    waiter_id
FROM InternalUser
WHERE 1=1
    AND login='$login'
    AND password='$password'