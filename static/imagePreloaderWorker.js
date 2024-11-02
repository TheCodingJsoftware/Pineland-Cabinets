// imagePreloaderWorker.js

self.onmessage = async function (event) {
    const { images } = event.data;

    for (const image of images) {
        try {
            const response = await fetch(image.url);
            const blob = await response.blob();
            const blobURL = URL.createObjectURL(blob);

            // Send the Blob URL back to the main thread as soon as it's ready
            self.postMessage({ id: image.id, blobURL });
        } catch (error) {
            console.error(`Error preloading image ${image.id}:`, error);
            self.postMessage({ id: image.id, error: true });
        }
    }
};
