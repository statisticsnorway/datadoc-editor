{
  description = "dev environment for datadoc-editor";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = inputs @ {
    flake-parts,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin"];
      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: {
        devShells.default = pkgs.mkShell {
          name = "datadoc-editor";
          packages = with pkgs; [
            python3
            uv
            python313Packages.ruff
            python313Packages.nox
          ];
        };
        formatter = pkgs.alejandra;
      };
    };
}
