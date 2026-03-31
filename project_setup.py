import subprocess
import time


def setup_project():
    compose_cmd = ["docker", "compose", "up", "-d"]
    container_name = "cosc_301_proj_postgres_1"
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
                    time.sleep(4)
                    return True
        except Exception as e:
            print(f"Error checking container status: {e}")
        time.sleep(1)
    print("Timeout waiting for the postgres container to be up.")
    return False
