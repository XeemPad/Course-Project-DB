SELECT
    idExtUser,
    login,
    user_group
FROM ExternalUser
WHERE 1=1
    AND login='$login'
    AND password='$password';