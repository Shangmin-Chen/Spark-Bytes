# Spark! Bytes

## Overview
Spark Bytes is a web application designed for Boston University students and faculty to post events that offer free food or snacks. The goal is to minimize food waste by making surplus food from events more accessible to the BU community. This initiative not only helps students find free food but also promotes sustainability by reducing the waste generated from over-purchasing food for campus events.

## Features
- **User Authentication**  
  Users can register, log in, and manage their profiles. In addition to traditional email and password authentication, the application integrates with **Auth0** for secure and seamless third-party authentication. This allows users to log in using services like Google, Facebook, or other supported providers.

- **Event Posting and Allergy Information**  
  Organizers can create event posts with details like time, location, type of food, and any additional information such as allergy warnings or dietary options (e.g., nut-free, gluten-free, vegan). This ensures attendees are informed and can choose events that suit their dietary needs.

- **Event Discovery**  
  Students and faculty can browse upcoming events offering free food using an intuitive interface.

- **Registration and QR Codes**  
  When users sign up for an event, they receive an email confirmation that includes a QR code. This QR code can be scanned at the event for easy check-in and tracking attendance.

- **Interactive Map**  
  Users can view events on an integrated map, making it easy to locate nearby events and navigate to them.

- **Sustainability Focus**  
  Designed to help minimize food waste by ensuring leftover food is consumed rather than discarded.


## Prerequisites

Before installing Spark Bytes, ensure you have the following installed on your system:

- **Python 3.10** or higher
- **Node.js** (v14 or higher) and **npm** (for frontend dependencies)
- **Git** (for cloning the repository)

### Verify Prerequisites

Check your installations:

```bash
python3 --version  # Should show Python 3.10 or higher
node --version     # Should show v14 or higher
npm --version      # Should show npm version
git --version      # Should show git version
```

## Installation

Follow these steps to set up Spark Bytes on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/Shangmin-Chen/Spark-Bytes.git
cd Spark-Bytes
```

### 2. Create and Activate Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

**On macOS/Linux:**
```bash
python3.10 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python3.10 -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when the virtual environment is active.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
npm install
```

This installs the Auth0 SPA JavaScript SDK required for authentication.

### 5. Set Up Environment Variables

Create a `.env` file in the `spark_bytes` directory:

```bash
cd spark_bytes
cp .env.example .env
```

Then edit the `.env` file and fill in all the required values:

- **SECRET_KEY**: Generate a Django secret key using:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  Copy the output and paste it as the value for `SECRET_KEY` in your `.env` file.

- **EMAIL_HOST_USER** and **EMAIL_HOST_PASSWORD**: 
  - Use your Gmail address for `EMAIL_HOST_USER`
  - Generate a Gmail App Password at https://myaccount.google.com/apppasswords
  - Use the app password (not your regular Gmail password) for `EMAIL_HOST_PASSWORD`

- **GOOGLE_MAPS_API_KEY**: 
  - Get your API key from https://console.cloud.google.com/apis/credentials
  - Enable the Maps JavaScript API and Places API in your Google Cloud project

- **AUTH0 Configuration** (AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL, AUTH0_API_IDENTIFIER):
  - Create an account at https://auth0.com/
  - Create a new application in your Auth0 dashboard
  - Set the callback URL to `http://127.0.0.1:8000/auth0/callback/` for local development
  - Copy the domain, client ID, and client secret from your Auth0 application settings
  - Create an API in Auth0 and use its identifier for `AUTH0_API_IDENTIFIER`

**Important:** Make sure you're back in the project root directory before proceeding:

```bash
cd ..
```

### 6. Run Database Migrations

Set up the database schema:

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin username, email, and password.

## Running the Application

### Development Mode

1. **Make sure your virtual environment is activated:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

3. **Open your web browser:**
   Visit: http://127.0.0.1:8000/

4. **Test the application:**
   - Create an account or log in with Auth0
   - Browse events and view them on the map
   - Create a new event (if logged in)
   - Register for an event to receive a confirmation email with QR code

**Note:** The development server will automatically reload when you make changes to your code. Press `Ctrl+C` in the terminal to stop the server.

## Production Server

To run the application in production mode:

1. **Set Production Environment Variables:**
   Make sure your `.env` file has production settings:
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=PROD_WEBSITE,127.0.0.1,localhost
   AUTH0_CALLBACK_URL=https://PROD_WEBSITE/auth0/callback/
   ```
   Ensure all other required environment variables are set (SECRET_KEY, AUTH0_*, EMAIL_*, etc.)

2. **Collect Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the Production Server with Gunicorn:**
   ```bash
   gunicorn spark_bytes.wsgi --bind 0.0.0.0:8000
   ```
   
   For better production setup, you can use additional options:
   ```bash
   gunicorn spark_bytes.wsgi --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile -
   ```

5. **Using a Process Manager (Recommended):**
   For production deployments, consider using a process manager like `systemd` or `supervisor` to keep the server running and automatically restart on failure.

6. **Reverse Proxy Setup:**
   It's recommended to use a reverse proxy like Nginx or Apache in front of Gunicorn for better performance, SSL termination, and static file serving.

## Deployment

Visit [Spark Bytes Live Demo](spark-bytes.shangmin.me)

## Presentation link
https://docs.google.com/presentation/d/1WUJ4NKX85KHb8Ybb-ZKkAWRyvcUgOTfjAsP78a053Vw/edit?usp=sharing

## Future Enhancements
- **Enhanced Authentication Options**  
  Expanding the use of **Auth0** to include additional third-party providers and multi-factor authentication (MFA) for improved security.

- **Mobile App Integration**  
  Developing a dedicated mobile app for iOS and Android to enhance accessibility and user experience.

- **Real-Time Event Updates**  
  Adding real-time notifications for new or nearby events, dynamically updating event details and availability.

- **Personalized Recommendations**  
  Implementing machine learning to suggest events based on user preferences, location, and past activity.

- **Gamification Features**  
  Introducing a rewards system for users who frequently attend events or post events, fostering greater engagement.

- **Food Analytics Dashboard**  
  Providing organizers with insights into food waste reduction, attendance statistics, and feedback to improve future events.

- **Community Collaboration**  
  Allowing users to collaborate by pooling leftover food from smaller events or individual contributions, expanding the reach of the platform.
