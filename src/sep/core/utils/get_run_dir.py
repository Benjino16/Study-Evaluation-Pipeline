import os

def get_list_of_run_paths(base_dir: str):
    run_paths = []
    base_dir = os.path.abspath(base_dir)

    for root, dirs, files in os.walk(base_dir):
        # Verzeichnisse, die mit "run-" anfangen, herausfiltern
        run_dirs = [d for d in dirs if d.startswith("run-")]

        for rd in run_dirs:
            abs_path = os.path.join(root, rd)
            rel_path = os.path.relpath(abs_path, base_dir)
            run_paths.append(rel_path)

        # Verhindern, dass os.walk weiter in Run-Directories hineinläuft
        dirs[:] = [d for d in dirs if not d.startswith("run-")]

    return run_paths