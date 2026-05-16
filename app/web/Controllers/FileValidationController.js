class FileValidationController {
    constructor(filepath) {
        this.filepath = filepath;
        this.errors = [];
    }

    validatePath() {
        if (this.isAbsolutePath(this.filepath)) return false;

        const parts = this.splitPathIntoParts();
        for (const part of parts) {
            if (part === "..") {
                this.registerError("Path must not contain '..'");
            } else {
                if (this.verifyPathAgainstOS(part)) {
                    if (!this.verifyPathAgainstFileSystem(part)) {
                        this.registerError(`Path part '${part}' isn't valid in this file system.`);
                    }
                } else {
                    this.registerError(`Path part '${part}' is not valid on this OS.`);
                }
            }
        }

        return this.errors.length === 0;
    }

    isAbsolutePath(filepath) {
        const isAbsolute =
        /^[A-Za-z]:[\\\/]/.test(filepath) ||
        filepath.startsWith("\\\\") ||
        filepath.startsWith("/");

        if (isAbsolute) {
            this.registerError("Path must not be absolute.");
            return true;
        }
        return false;
    }

    splitPathIntoParts() {
        const sep = window.OS_NAME === "Windows" ? "\\" : "/";
        return this.filepath.split(sep);
    }

    registerError(message) {
        this.errors.push(message);
    }

    verifyPathAgainstOS(part) {
        if (!part) return false;
        if (part.includes("\x00")) return false;

        if (window.OS_NAME === "Windows") {
            if (/[<>:"/\\|?*\x00-\x1f]/.test(part)) return false;
            if (/^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..+)?$/i.test(part)) return false;
        }

        return true;
    }

    verifyPathAgainstFileSystem(part, maxLen = 255) {
        if (!part) return false;

        const encoded = new TextEncoder().encode(part);
        if (encoded.length > maxLen) return false;

        if (window.FS_TYPE.includes("FAT") || window.FS_TYPE.includes("NTFS")) {
            if (part.endsWith(".") || part.endsWith(" ")) return false;
            if (/[<>:"/\\|?*\x00-\x1f]/.test(part)) return false;
        }

        return true;
    }
}
