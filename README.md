# Some Comments
The `advanced` implementation supports sending back-to-back text messages as shown in class. It also supports "uploading" image data through a socket and saving it. To do so, when the program is running on either end (i.e., the client-server connection is established), submit the following messaging `:UPLOAD: my_picture.jpeg`.

## A Few Caveats
1. If you're uploading from the client-side, the file (i.e., `my_picture.jpeg`) must be in the `client_dir` directory. If you're uploading from the server-side, then `server_dir`.
2. When the file is "uploaded" it will be stored in the other entity's directory (i.e., uploading from the client-side will have the server receive it and save the image in `server_dir`, and vice versa).
3. While this is not that cool or impressive in a local setting, try getting it to work across multiple devices (remember to make sure you have the server device's IP address and that both devices are on the same network).