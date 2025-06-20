{
  description = "Formal Containment project dev";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    parts.url = "github:hercules-ci/flake-parts";
    pantograph.url = "github:lenianiva/Pantograph";
  };
  outputs = { self, nixpkgs, parts, pantograph, }@inputs:
    parts.lib.mkFlake { inherit inputs; } {
      systems = [ "aarch64-darwin" "x86_64-linux" ];
      perSystem = { system, ... }: {
        devShells.default = let
          pkgs = import inputs.nixpkgs {
            inherit system;
            config.allowUnfree = true;
          };
          name = "Formal Containment dev";
          buildInputs = with pkgs; [
            elan
            uv
            typst
            typstyle
            nodejs_24
            lefthook
            pandoc
            pantograph.packages.${system}.executable
            util-linux  # ionice
            claude-code
          ];
        in pkgs.mkShell { inherit name buildInputs; };
      };
    };
}
