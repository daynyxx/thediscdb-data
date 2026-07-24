{
  description = "ImportBuddy - DiscDB data import tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonWithDeps = pkgs.python314.withPackages (ps: [
          ps.requests
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonWithDeps
            pkgs.python314
            pkgs.python314Packages.pytest
            pkgs.python314Packages.pytest-mock
          ];

          shellHook = ''
            echo "Python: $(which python)"
            echo "Pytest: $(which pytest)"
          '';
        };

        apps.default = {
          type = "app";
          program = toString (pkgs.writeShellApplication {
            name = "import-buddy";
            runtimeInputs = [ pythonWithDeps ];
            text = ''
              exec python import_buddy.py "$@"
            '';
          });
        };
      }
    );
}
