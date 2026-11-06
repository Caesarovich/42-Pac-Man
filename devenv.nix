{ pkgs, lib, config, inputs, ... }:

let
  raylibLibs = with pkgs; [
    xorg.libX11
    xorg.libXcursor
    xorg.libXi
    xorg.libXinerama
    xorg.libXrandr
    libGL
    libglvnd
    mesa
    wayland
    wayland-protocols
    libxkbcommon
  ];
in
{
    packages = raylibLibs;
    env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath raylibLibs;

    languages.python = {
        enable = true;
        version = "3.14";
        venv.enable = true;
        lsp.package = pkgs.python3Packages.python-lsp-server;
        uv = {
            enable = true;
            sync.enable = true;
        };
    };
    
    scripts= {
        format-check = {
            exec = ''
                ruff format --check .
            '';
            packages = [ pkgs.ruff ];
            description = "Run checks for the formatter";
        };
        format-fix = {
            exec = ''
                ruff format .
            '';
            packages = [ pkgs.ruff ];
            description = "Run auto-fixes for the formatter";
        };
        type-check = {
            exec = ''
                ty check
            '';
            packages = [ pkgs.ty ];
            description = "Run checks for type hints";
        };
        lint-check = {
            exec = ''
                ruff check .
            '';
            packages = [ pkgs.ruff ];
            description = "Run checks for the linter";
        };
        lint-fix = {
            exec = ''
                ruff check --fix .
            '';
            packages = [ pkgs.ruff ];
            description = "Run auto-fixes for the linter";
        };
    };
}
