import os
import sqlite3

import psycopg
from django.contrib.auth.hashers import make_password


SQLITE_DB = "db.sqlite3"

POSTGRES_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "profiles_db",
    "user": "profiles_user",
    "password": os.environ["POSTGRES_PROFILES_PASSWORD"],
}


def is_django_password_hash(value):
    """Return True when the value already looks like a Django password hash."""
    return value.startswith(("pbkdf2_sha256$", "argon2$", "bcrypt$", "scrypt$"))


def main():
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row

    users = sqlite_conn.execute(
        """
        SELECT
            id,
            password,
            last_login,
            is_superuser,
            email,
            name,
            is_active,
            is_staff,
            email_verified
        FROM profiles_api_userprofile
        ORDER BY id
        """
    ).fetchall()

    feed_items = sqlite_conn.execute(
        """
        SELECT
            id,
            status_text,
            created_on,
            user_profile_id
        FROM profiles_api_profilefeeditem
        ORDER BY id
        """
    ).fetchall()

    print(f"SQLite users found: {len(users)}")
    print(f"SQLite feed items found: {len(feed_items)}")

    with psycopg.connect(**POSTGRES_CONFIG) as conn:
        with conn.transaction():
            with conn.cursor() as cursor:
                for user in users:
                    password = user["password"]

                    if not is_django_password_hash(password):
                        password = make_password(password)

                    cursor.execute(
                        """
                        INSERT INTO profiles_api_userprofile
                        (
                            id,
                            password,
                            last_login,
                            is_superuser,
                            email,
                            name,
                            is_active,
                            is_staff,
                            email_verified
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            user["id"],
                            password,
                            user["last_login"],
                            bool(user["is_superuser"]),
                            user["email"],
                            user["name"],
                            bool(user["is_active"]),
                            bool(user["is_staff"]),
                            bool(user["email_verified"]),
                        ),
                    )

                for item in feed_items:
                    cursor.execute(
                        """
                        INSERT INTO profiles_api_profilefeeditem
                        (
                            id,
                            status_text,
                            created_on,
                            user_profile_id
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            item["id"],
                            item["status_text"],
                            item["created_on"],
                            item["user_profile_id"],
                        ),
                    )

                cursor.execute(
                    """
                    SELECT setval(
                        pg_get_serial_sequence(
                            'profiles_api_userprofile',
                            'id'
                        ),
                        COALESCE(
                            (SELECT MAX(id) FROM profiles_api_userprofile),
                            1
                        ),
                        true
                    )
                    """
                )

                cursor.execute(
                    """
                    SELECT setval(
                        pg_get_serial_sequence(
                            'profiles_api_profilefeeditem',
                            'id'
                        ),
                        COALESCE(
                            (SELECT MAX(id) FROM profiles_api_profilefeeditem),
                            1
                        ),
                        true
                    )
                    """
                )

    sqlite_conn.close()

    print("Migration completed successfully.")
    print(f"Users migrated: {len(users)}")
    print(f"Feed items migrated: {len(feed_items)}")


if __name__ == "__main__":
    main()
