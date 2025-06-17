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
      perSystem = { pkgs, ... }: {
        devShells.default = let
          name = "Formal Containment dev";
          buildInputs = with pkgs; [
            elan
            uv
            typst
            typstyle
            nodejs_24
            lefthook
            pandoc
            pantograph.packages.${pkgs.system}.executable
            util-linux  # ionice
          ];
        in pkgs.mkShell { inherit name buildInputs; };
      };
    };
}
