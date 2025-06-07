import subprocess
import datetime

def get_ollama_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.strip().split('\n')

        # Skip the header row (e.g. "NAME           SIZE    MODIFIED")
        header = lines[0]
        model_lines = lines[1:]

        models = []
        for line in model_lines:
            # Split line by multiple spaces or tabs
            parts = line.split()
            if len(parts) < 3:
                continue

            name = parts[0]
            size_str = parts[1]
            modified_str = " ".join(parts[2:])  # The rest of the line

            # Try to parse the size into bytes (basic, not exact)
            size = parse_size(size_str)

            # Try to parse datetime or return string
            try:
                modified_at = datetime.datetime.strptime(modified_str, "%Y-%m-%dT%H:%M:%S.%f%z").isoformat()
            except:
                modified_at = modified_str  # fallback to raw string

            models.append({
                "name": name,
                "modified_at": modified_at,
                "size": size,
                "digest": None,
                "details": {
                    "format": "gguf",
                    "family": "llama",
                    "families": None,
                    "parameter_size": "",
                    "quantization_level": "Q4_0"
                }
            })

        return {"models": models}

    except subprocess.CalledProcessError as e:
        print("Error running ollama:", e)
        return {"models": []}
    except Exception as e:
        print("Unexpected error:", e)
        return {"models": []}


def parse_size(size_str):
    """Convert size like '3.5GB' to bytes"""
    try:
        size_str = size_str.upper()
        if "GB" in size_str:
            return int(float(size_str.replace("GB", "")) * 1e9)
        elif "MB" in size_str:
            return int(float(size_str.replace("MB", "")) * 1e6)
        elif "KB" in size_str:
            return int(float(size_str.replace("KB", "")) * 1e3)
        else:
            return int(size_str)
    except:
        return 0
