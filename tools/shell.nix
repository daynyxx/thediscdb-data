{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    (pkgs.python314.withPackages (python-pkgs: [
      python-pkgs.requests
    ]))
    pkgs.python314
    pkgs.python314Packages.pytest
    pkgs.python314Packages.pytest-mock
  ];

  shellHook = ''
    echo "Python: $(which python)"
    echo "Pytest: $(which pytest)"
  '';
}
