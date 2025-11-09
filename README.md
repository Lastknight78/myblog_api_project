# MyBlog

**MyBlog** is a role-based blogging platform with user and admin roles. Itallows users to create, manage, and interact with blog posts while providing administrators the ability to manage users and content. The project uses **PostgreSQL** as the database (via **neon.tech**), **Mega.nz** for cloud storage, and is deployed on **Render**.

## Features

- **Implemented User Authentication**: Signup, login, password reset, profile management with JWT authentication.
- **Developed Blog Post Features**: CRUD operations for posts, hashtag categorization, like/dislike functionality, and comment management.
- **Admin Dashboard**: Allowed admin users to manage user accounts (block, deactivate, delete) and monitor platform activity.
- **Cloud Integration**: Used Mega.nz for cloud storage of media files (profile images and post media).
- **Deployed on Render**: Leveraged Render for continuous deployment and PostgreSQL (neon.tech) as the database backend.
- **API Documentation:** Full API available at [MyBlog Docs](https://myblog-ysd9.onrender.com/docs).

## Technology Stack

- **Backend Framework:** FastAPI (Python)
- **Database:** PostgreSQL (via neon.tech)
- **Cloud Storage:** Mega.nz
- **Deployment:** Render

## Endpoints

### Auth Router

1. **Login (JWT-based):**  
   `POST /api/auth/login/`  
   Users can log in using their email and password. The response includes a JWT token for authentication.

2. **Signup:**  
   `POST /api/auth/signup/`  
   Users can sign up with their email. An activation email will be sent for account verification.

3. **Check User Profile:**  
   `GET /api/auth/users/profile/`  
   Fetch the profile of the currently authenticated user.

4. **Update User Profile:**  
   `PUT /api/auth/users/update-profile/`  
   Update profile details of the authenticated user (e.g., name, bio, etc.).

5. **Reset Password:**  
   `POST /api/auth/users/forget-password/`  
   Initiate password reset by sending an email to the user with a reset link.

6. **Change Email:**  
   `POST /api/auth/users/change-email/{new_email}/`  
   Change the authenticated user’s email address. An email verification will be required.

7. **Change Password:**  
   `POST /api/auth/users/change-password/{new_password}/`  
   Allows the user to change their password once authenticated.

8. **Delete User (Admin Only):**  
   `DELETE /api/auth/delete/{user_id}`  
   Admins can delete any user by their user ID.

9. **Deactivate/Block User (Admin Only):**  
   `GET /api/auth/users/{user_id}/deactivate/`  
   Admins can block or deactivate a user, restricting access to their account.

10. **Get All Users (Admin Only):**  
    `GET /api/auth/all-users/`  
    Retrieve a list of all registered users for admin management purposes.

### Post Router

1. **Create a Blog Post:**  
   `POST /api/posts/`  
   Authenticated users can create a new blog post. Posts can include hashtags for categorization.

2. **Get a Single Post:**  
   `GET /api/posts/{post_id}`  
   Retrieve a specific blog post by its ID.

3. **Get All Posts:**  
   `GET /api/posts/`  
   Fetch all blog posts, optionally with filters like date or hashtags.

4. **Get All Posts of a User:**  
   `GET /api/posts/users/`  
   Retrieve all blog posts created by a specific user.

5. **Edit a Post:**  
   `PUT /api/posts/{post_id}/`  
   Edit the contents of an existing blog post (must be the post’s creator).

6. **Delete a Post:**  
   `DELETE /api/posts/{post_id}/`  
   Delete a blog post (must be the post’s creator or an admin).

7. **Get Posts with Hashtag:**  
   `GET /api/posts/hashtags/{hashtag}`  
   Fetch all posts containing a specific hashtag.

8. **Add a Comment to a Post:**  
   `POST /api/posts/{post_id}/comments/`  
   Users can add comments to a blog post.

9. **Edit Comment:**  
   `PUT /api/posts/{post_id}/comments/{comment_id}/`  
   Edit a specific comment on a blog post (must be the comment’s author).

10. **Delete Comment:**  
    `DELETE /api/posts/{post_id}/comments/{comment_id}/`  
    Delete a specific comment from a blog post (must be the comment’s author or an admin).

11. **Like a Post:**  
    `POST /api/posts/{post_id}/like/`  
    Users can like a post, increasing its like count.

12. **Dislike a Post:**  
    `POST /api/posts/{post_id}/dislike/`  
    Users can dislike a post, increasing its dislike count.

13. **Remove Like from a Post:**  
    `DELETE /api/posts/{post_id}/like/`  
    Remove the like from a post (if previously liked).

14. **Remove Dislike from a Post:**  
    `DELETE /api/posts/{post_id}/dislike/`  
    Remove the dislike from a post (if previously disliked).

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SOO2023/myblog_api.git
   cd myblog

   ```

2. **Create a virtual environment:**

   ```bash
   # For Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate

   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   DEFAULT_PROFILE_IMAGE
   SECRET_KEY
   ALGORITHM
   DB_URL
   MAIL_USERNAME
   MAIL_PASSWORD
   MAIL_FROM
   MAIL_PORT
   MAIL_SERVER
   MAIL_FROM_NAME
   HOST_SERVER
   MEGA_PASSWORD
   PROFLE_IMAGE_FOLDER
   POST_IMAGE_FOLDER
   ```

5. **Run the application:**

   ```bash
   uvicorn src.main:app --reload
   ```

6. **Run the application:**

   ```bash
   http://127.0.0.1:8000/docs
   ```
