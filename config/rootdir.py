from project_paths import PROJECT_ROOT


# Backward compatibility for older extensions. New code should import the
# pathlib-based constants from config.paths instead.
root_dir = str(PROJECT_ROOT)
