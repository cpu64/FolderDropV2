class FileUploadController {
    constructor(file) {
        this.file = file;

        this.chunkSize = 10 * 1024 * 1024;

        this.maxConcurrentUploads = 6;

        this.maxRetries = 5;

        this.chunks = [];

        this.filepath = CURRENT_PATH
            ? `${CURRENT_PATH}/${file.name}`
            : file.name;
    }

    async start_uploading() {

        const validator = new FileValidationController(
            this.filepath
        ); // 58.1 jeigu tik tiek siejasi su FileValidationController, tai ten yra dependency, ne asociacija

        const isValid = validator.validatePath();

        if (!isValid) {
            return {
                ok: false,
                errors: validator.errors,
            };
        }

        this.splitIntoChunks();

        const metadata = {
            filepath: this.filepath,
            part_count: this.chunks.length,
        };

        try {

            const metadataResponse = await fetch(
                "/api/recieve-metadata",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(metadata),
                }
            );

            if (!metadataResponse.ok) {
                return {
                    ok: false,
                    errors: [
                        "Failed to send metadata to server.",
                    ],
                };
            }

            await this.uploadAllParts();

            return {
                ok: true,
                partCount: this.chunks.length,
            };

        } catch (error) {
            return {
                ok: false,
                errors: [error.message],
            };
        }
    }

    async uploadAllParts() {

        let nextPartIndex = 0;

        const workers = [];

        const worker = async () => {

            while (true) {

                const currentIndex = nextPartIndex++;

                if (currentIndex >= this.chunks.length) {
                    return;
                }

                await this.uploadPartWithRetry(
                    currentIndex
                );
            }
        };

        for (
            let i = 0;
            i < this.maxConcurrentUploads;
            i++
        ) {
            workers.push(worker());
        }

        await Promise.all(workers);
    }

    async uploadPartWithRetry(partNumber) {

        let lastError = null;

        for (
            let attempt = 1;
            attempt <= this.maxRetries;
            attempt++
        ) {

            try {

                await this.uploadPart(partNumber);

                return;

            } catch (error) {

                lastError = error;

                console.warn(
                    `Part ${partNumber} upload failed ` +
                    `(attempt ${attempt}/${this.maxRetries})`,
                    error
                );

                await this.sleep(1000);
            }
        }

        throw new Error(
            `Part ${partNumber} failed after ` +
            `${this.maxRetries} retries: ${lastError}`
        );
    }

    async uploadPart(partNumber) {

        const formData = new FormData();

        formData.append(
            "filepath",
            this.filepath
        );

        formData.append(
            "part_number",
            partNumber
        );

        formData.append(
            "data",
            this.chunks[partNumber]
        );

        const response = await fetch(
            "/api/recieve-part",
            {
                method: "POST",
                body: formData,
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const result = await response.json();

        if (!result.ok) {
            throw new Error(
                result.error || "Upload failed"
            );
        }

        return result;
    }

    splitIntoChunks() {

        this.chunks = [];

        let start = 0;

        while (start < this.file.size) {

            const end = Math.min(
                start + this.chunkSize,
                this.file.size
            );

            const chunk = this.file.slice(
                start,
                end
            );

            this.chunks.push(chunk);

            start = end;
        }
    }

    sleep(ms) {
        return new Promise(
            resolve => setTimeout(resolve, ms)
        );
    }
}
