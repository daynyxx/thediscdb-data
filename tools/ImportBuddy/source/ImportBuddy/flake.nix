{
  description = "Simple .NET development environment (x86_64‑linux)";

  # ----------------------------------------------------------------------
  # INPUTS
  # ----------------------------------------------------------------------
  # Pull the latest unstable channel – you can pin a specific commit if you
  # need reproducibility.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  # ----------------------------------------------------------------------
  # OUTPUTS
  # ----------------------------------------------------------------------
  outputs = { self, nixpkgs }: let
    # Import nixpkgs for the x86_64‑linux platform.
    pkgs = import nixpkgs { system = "x86_64-linux"; };
  in {

    # ------------------------------------------------------------------
    # DEVELOPMENT SHELL
    # ------------------------------------------------------------------
    devShells.x86_64-linux.default = pkgs.mkShell {

      # --------------------------------------------------------------
      # 2️⃣ Add any extra utilities you commonly use while developing.
      # --------------------------------------------------------------
      nativeBuildInputs = [
        pkgs.dotnet-sdk_9
        pkgs.dotnet-runtime_9
        pkgs.git
        pkgs.curl
        pkgs.sqlite                     # optional native lib for packages that need it
      ];

      # --------------------------------------------------------------
      # 3️⃣ Friendly startup message.
      # --------------------------------------------------------------
      shellHook = ''
        # Ensure the selected SDK is first on $PATH.
        export PATH=${pkgs.dotnet-sdk_9}/bin:$PATH

        echo ""
        echo "🚀  .NET development environment (x86_64‑linux) ready"
        echo "   • SDK version: $(dotnet --version)"
        echo "   • Useful commands:"
        echo "       dotnet restore   # fetch NuGet packages"
        echo "       dotnet build     # compile the solution/project"
        echo "       dotnet test      # run tests"
        echo "   • Extra tools: git, curl, sqlite"
        echo ""
      '';
    };

    # ------------------------------------------------------------------
    # OPTIONAL ONE‑LINE BUILD APP
    # ------------------------------------------------------------------
    # Uncomment the block below if you’d like to run `nix run .#build`
    # to invoke `dotnet build` without first entering a shell.
    # ------------------------------------------------------------------
    # apps.x86_64-linux.build = {
    #   type = "app";
    #   program = pkgs.writeShellScript "dotnet-build" ''
    #     set -euo pipefail
    #     export PATH=${pkgs.dotnet-sdk_7}/bin:$PATH
    #     if ls *.sln 1>/dev/null 2>&1; then
    #       dotnet build *.sln "$@"
    #     else
    #       dotnet build "$@"
    #     fi
    #   '';
    # };
  };
}
