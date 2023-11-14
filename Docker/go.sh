#!/bin/bash

# Specify the name of the Docker image tarball
IMAGE_TAR="submission_lovi.tar.gz"

echo "Loading Image ..."
# Load the Docker image
docker load -i "$IMAGE_TAR"

# Check if the image was successfully loaded
if [ $? -eq 0 ]; then
    echo "Docker image loaded successfully."
    image_id=$(docker images -q | head -n 1)

    # Run a container from the loaded image with port mapping to 7080 and capture the Container ID
    CONTAINER_ID=$(docker run -d -p 7080:7080 -v /Users/hahuy/Desktop/Huy/VLSP23/abc/test.lo:/app/input.vi.subword $image_id)
                                    #<Path to input file on your local device>:/app/input.vi.subword
    echo "Container started with ID: $CONTAINER_ID"

    # Wait for the container to finish
    docker wait "$CONTAINER_ID"

    echo "Container logs"

    docker logs "$CONTAINER_ID"

    # Extract a file from the running container
    docker cp "$CONTAINER_ID:/app/UN.vi.translated.desubword" /Users/hahuy/Desktop/Huy/VLSP23/abc/
                                                        

    # Check if the file extraction was successful
    if [ $? -eq 0 ]; then
        echo "File extracted successfully."
    else
        echo "Error: Failed to extract the file."
    fi

else
    echo "Error: Failed to load the Docker image."
fi
