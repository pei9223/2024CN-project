class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:rootpassword@db/labapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # file max 16MB

    # jwt
    JWT_SECRET_KEY="xxxx"

    DEBUG=False
    # EMAIL SETTINGS
    MAIL_DEBUG=False
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_DEFAULT_SENDER=('admin', 'peichun23.cs12@nycu.edu.tw')
    MAIL_MAX_EMAILS=10
    MAIL_USERNAME='peichun23.cs12@nycu.edu.tw'
    MAIL_PASSWORD='xxxx'
