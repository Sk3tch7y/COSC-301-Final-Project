import subprocess
import time


def setup_project():
    compose_cmd = ["docker", "compose", "up", "-d"]
    container_name = "cosc_301_proj_postgres_1"
    db_name = "financial_data"
    db_user = "postgres"
    db_password = "other_pw"
    timeout = 60  # seconds

    try:
        subprocess.run(compose_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running docker compose up: {e}")
        return False

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Get the container status
            ps_cmd = [
                "docker",
                "ps",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.Status}}",
            ]
            result = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            status = result.stdout.strip()
            if status:
                if status.startswith("Up"):
                    try:
                        # Persisted Postgres volumes keep the original password.
                        # Re-apply the expected password and ensure the target DB exists.
                        subprocess.run(
                            [
                                "docker",
                                "exec",
                                container_name,
                                "psql",
                                "-U",
                                db_user,
                                "-d",
                                "postgres",
                                "-c",
                                f"ALTER USER {db_user} WITH PASSWORD '{db_password}';",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        db_exists = subprocess.run(
                            [
                                "docker",
                                "exec",
                                container_name,
                                "psql",
                                "-U",
                                db_user,
                                "-d",
                                "postgres",
                                "-tAc",
                                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        if db_exists.stdout.strip() != "1":
                            subprocess.run(
                                [
                                    "docker",
                                    "exec",
                                    container_name,
                                    "psql",
                                    "-U",
                                    db_user,
                                    "-d",
                                    "postgres",
                                    "-c",
                                    f"CREATE DATABASE {db_name};",
                                ],
                                check=True,
                                capture_output=True,
                                text=True,
                            )
                    except subprocess.CalledProcessError as e:
                        print(f"Error preparing postgres credentials/database: {e.stderr.strip()}")
                        return False
                    time.sleep(4)
                    return True
        except Exception as e:
            print(f"Error checking container status: {e}")
        time.sleep(1)
    print("Timeout waiting for the postgres container to be up.")
    return False
