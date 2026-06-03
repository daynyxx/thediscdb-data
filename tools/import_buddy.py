from config import load_config
from workflows import run_import, run_finalize, run_calc_hash, setup_config


def main() -> None:
    cfg = load_config()

    while True:
        print("\n=== ImportBuddy ===")
        print("  [1] Import")
        print("  [2] Finalize")
        print("  [3] Calculate Hash")
        print("  [4] Setup")
        print("  [5] Exit")

        choice = input("\nChoice: ").strip()
        if choice == "1":
            run_import(cfg)
        elif choice == "2":
            run_finalize(cfg)
        elif choice == "3":
            run_calc_hash(cfg)
        elif choice == "4":
            setup_config(cfg)
        elif choice == "5":
            break


if __name__ == "__main__":
    main()