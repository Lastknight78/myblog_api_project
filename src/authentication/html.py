def verification_email_html(user, reset_link) -> tuple[str, str]:
    subject = "MyBlog - Reset Passowrd"
    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body style="background-color: #f8f9fa; padding: 20px;">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card border-0 shadow-sm">
                            <div class="card-header bg-success text-white text-center">
                                <h2>Password Reset</h2>
                            </div>
                            <div class="card-body">
                                <p>Hello {user.firstname.capitalize()},</p>
                                <p>We received a request to reset your password. Click the button below to reset it:</p>
                                <div class="text-center">
                                    <a href="{reset_link}" class="btn btn-success">Reset Password</a>
                                </div>
                                <p class="mt-3">If you did not request a password reset, please ignore this email.</p>
                                <p>Thank you,<br>MyBlog</p>
                            </div>
                            <div class="card-footer text-center text-muted">
                                &copy; 2024 MyBlog. All rights reserved.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.6.0/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
    """
    return html, subject


def activate_account_html(user, activation_link) -> tuple[str, str]:
    subject = "MyBlog - Activate Your Account"
    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Activate Your Account</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{
                    background-color: #f8f9fa;
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 30px;
                }}
                .btn-primary {{
                    background-color: #28a745;
                    border: none;
                }}
                .btn-primary:hover {{
                    background-color: #218838;
                }}
                .footer-text {{
                    font-size: 0.875rem;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container email-container">
                <h2 class="text-center mb-4">Activate Your Account</h2>
                <p>Hello {user.firstname},</p>
                <p>Thank you for signing up with MyBlog! To complete your registration and activate your account, please click the button below:</p>
                <div class="text-center my-4">
                    <a href="{activation_link}" class="btn btn-primary btn-lg">Activate Account</a>
                </div>
                <p>If you did not sign up for an account, please disregard this email or let us know.</p>
                <p class="mt-4">Welcome to the MyBlog community!</p>
                <p>Best regards,<br>The MyBlog Team</p>
                <hr>
                <p class="text-center footer-text">If the button above doesn't work, copy and paste the following link into your browser:</p>
                <p class="text-center footer-text">
                    <a href="{activation_link}" style="color: #007bff;">{activation_link}</a>
                </p>
                <hr>
                <p class="text-center footer-text mt-4">&copy; 2024 MyBlog. All rights reserved.</p>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
    return html, subject
