# 📝 Blogs API

A production-ready blog REST API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT authentication** with full Role-Based Access Control (RBAC).

---

## ✨ Features

- 🔐 **Authentication** — Register, Login, Email Verification, Password Reset
- 🔑 **OAuth2** — Google OAuth login
- 👥 **RBAC** — Role-Based Access Control with dynamic permissions and OAuth2 scopes
- 📝 **Posts** — Full CRUD with slug generation, categories, tags, auto author promotion
- 💬 **Comments** — Nested replies with moderation
- ❤️ **Likes** — Toggle like/unlike on posts and comments
- 🔖 **Bookmarks** — Save posts for later
- 🔔 **Notifications** — Real-time notifications for likes, comments, replies, bookmarks
- 🖼️ **File Upload** — Cloudinary integration for avatars and thumbnails
- 🛡️ **Admin Dashboard** — Stats, ban users, assign roles
- 🐳 **Docker** — Fully containerized with docker-compose

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (Async) |
| Migrations | Alembic |
| Auth | JWT + OAuth2 Scopes |
| Password | Bcrypt |
| Email | FastAPI-Mail |
| File Storage | Cloudinary |
| Containerization | Docker + Docker Compose |
| Testing | Pytest + HTTPX |

---

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/blogs-api.git
cd blogs-api

# 2. Copy environment variables
cp .env.example .env
# Fill in your credentials in .env

# 3. Build and start
docker-compose up --build

# 4. API is running at
http://localhost:8000

# 5. Swagger docs
http://localhost:8000/docs
```

### Without Docker

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/blogs-api.git
cd blogs-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env
# Fill in your credentials in .env

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload

# 7. API is running at
http://localhost:8000
```

---

## 📁 Project Structure

```
app/
├── core/
│   ├── config.py           ← environment settings
│   ├── security.py         ← JWT, hashing, token generation
│   ├── dependencies.py     ← get_current_user, OAuth2 scheme
│   ├── scopes.py           ← OAuth2 scopes + role-scope matrix
│   ├── cloudinary.py       ← file upload helpers
│   └── seed.py             ← seed roles, permissions, admin user
├── db/
│   ├── base.py             ← all model imports for Alembic
│   ├── session.py          ← async engine + session
│   └── migrations/         ← Alembic migration files
├── features/
│   ├── auth/               ← register, login, verify, OAuth
│   ├── users/              ← profile, update
│   ├── roles/              ← roles + permissions
│   ├── posts/              ← CRUD + publish
│   ├── categories/         ← CRUD (admin)
│   ├── tags/               ← CRUD (admin) + auto-create
│   ├── comments/           ← CRUD + nested replies
│   ├── likes/              ← toggle like
│   ├── bookmarks/          ← toggle bookmark
│   ├── notifications/      ← CRUD + mark as read
│   ├── uploads/            ← avatar + thumbnail upload
│   └── admin/              ← dashboard + ban + assign role
└── utilities/
    ├── baseResponse.py     ← standard API response wrapper
    └── exceptions.py       ← custom exception handlers
```

---

## 🗄️ Database Schema

```
users           ← core user model
roles           ← reader, author, editor, admin
permissions     ← granular permissions (post:create, post:publish...)
role_permissions← pivot: roles ↔ permissions
user_roles      ← pivot: users ↔ roles
oauth_accounts  ← Google/GitHub OAuth links
categories      ← post categories
tags            ← post tags
posts           ← blog posts
post_tags       ← pivot: posts ↔ tags
comments        ← nested comments (parent_id)
likes           ← polymorphic likes (post or comment)
bookmarks       ← saved posts
notifications   ← user notifications
```

---

## 🔐 RBAC — Roles & Permissions

| Permission | Reader | Author | Editor | Admin |
|---|---|---|---|---|
| `me:read` | ✅ | ✅ | ✅ | ✅ |
| `me:write` | ✅ | ✅ | ✅ | ✅ |
| `post:create` | ❌ | ✅ | ✅ | ✅ |
| `post:edit_own` | ❌ | ✅ | ✅ | ✅ |
| `post:edit_any` | ❌ | ❌ | ✅ | ✅ |
| `post:publish` | ❌ | ❌ | ✅ | ✅ |
| `post:delete_own` | ❌ | ✅ | ✅ | ✅ |
| `post:delete_any` | ❌ | ❌ | ❌ | ✅ |
| `comment:create` | ✅ | ✅ | ✅ | ✅ |
| `comment:delete_own` | ✅ | ✅ | ✅ | ✅ |
| `comment:delete_any` | ❌ | ❌ | ✅ | ✅ |
| `user:ban` | ❌ | ❌ | ❌ | ✅ |
| `admin:dashboard` | ❌ | ❌ | ❌ | ✅ |

### Auto Role Progression
```
Register  → reader  (automatic)
Create first post → author (automatic)
Admin promotes → editor / admin (manual)
```

---

## 📡 API Endpoints

### Auth
```
POST   /register                  ← register + send verification email
GET    /verify-email?token=       ← verify email
POST   /resend-verification       ← resend verification email
POST   /login                     ← login with email + password
POST   /token                     ← OAuth2 token endpoint (Swagger)
POST   /refresh                   ← refresh access token
POST   /forgot-password           ← send reset email
POST   /reset-password            ← reset password with token
GET    /auth/google/login         ← redirect to Google
GET    /auth/google/callback      ← Google OAuth callback
POST   /logout                    ← logout
```

### Users
```
GET    /users/me                  ← get my profile
PATCH  /users/me                  ← update my profile
```

### Posts
```
GET    /posts/                    ← get all published posts
GET    /posts/me                  ← get my posts
GET    /posts/{id}                ← get single post
POST   /posts/                    ← create post
PATCH  /posts/{id}                ← update post
PATCH  /posts/{id}/publish        ← publish post (editor/admin)
PATCH  /posts/{id}/unpublish      ← unpublish post (editor/admin)
DELETE /posts/{id}                ← delete post
```

### Categories
```
GET    /categories/               ← get all categories (public)
GET    /categories/{id}           ← get single category (public)
POST   /categories/               ← create category (admin)
PATCH  /categories/{id}           ← update category (admin)
DELETE /categories/{id}           ← delete category (admin)
```

### Tags
```
GET    /tags/                     ← get all tags (public)
GET    /tags/{id}                 ← get single tag (public)
POST   /tags/                     ← create tag (admin)
PATCH  /tags/{id}                 ← update tag (admin)
DELETE /tags/{id}                 ← delete tag (admin)
```

### Comments
```
GET    /posts/{id}/comments       ← get post comments + replies (public)
POST   /posts/{id}/comments       ← create comment or reply
PATCH  /posts/comments/{id}       ← update own comment
DELETE /posts/comments/{id}       ← delete comment (owner/editor/admin)
```

### Likes
```
POST   /posts/{id}/like           ← toggle like/unlike post
GET    /posts/{id}/like           ← get post likes count
POST   /comments/{id}/like        ← toggle like/unlike comment
GET    /comments/{id}/like        ← get comment likes count
```

### Bookmarks
```
GET    /bookmarks/                ← get my bookmarks
POST   /bookmarks/{post_id}       ← toggle bookmark
GET    /bookmarks/{post_id}/status← check bookmark status
```

### Notifications
```
GET    /notifications/            ← get my notifications
GET    /notifications/unread      ← get unread count
PATCH  /notifications/{id}/read   ← mark as read
PATCH  /notifications/read-all    ← mark all as read
DELETE /notifications/{id}        ← delete notification
```

### Uploads
```
POST   /uploads/avatar            ← upload user avatar
POST   /uploads/thumbnail         ← upload post thumbnail
```

### Roles
```
GET    /roles/                    ← get all roles (admin)
GET    /roles/{id}                ← get role with permissions (admin)
```

### Admin
```
GET    /admin/dashboard           ← stats (admin)
GET    /admin/users               ← all users (admin)
PATCH  /admin/users/{id}/ban      ← ban user
PATCH  /admin/users/{id}/unban    ← unban user
PATCH  /admin/users/{id}/assign-role  ← assign role
PATCH  /admin/users/{id}/revoke-role  ← revoke role
```

---

## 🌍 Environment Variables

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=blogs
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/blogs

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Gmail)
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your@gmail.com
MAIL_FROM_NAME=Blogs API
FRONTEND_URL=http://localhost:3000

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/features/auth/test_register.py -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up --build -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Reset database
docker-compose down -v

# Access container shell
docker exec -it blogs_api bash
```

---

## 📄 License

MIT License — feel free to use this project for learning or as a base for your own blog API.
