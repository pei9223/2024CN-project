# Flask Application API Documentation

---

## User Registration

- **Endpoint:** `/api/register`
- **Method:** POST
- **Description:** Registers a new user.
- **Content type:** application/json
- **Parameters:**
  - `userID` (string, required): Unique identifier for the user.
  - `userPassword` (string, required): Password for the user account.
  - `dep` (string, required): Department of the user. Allowed values: 'Fab A', 'Fab B', 'Fab C', 'chemical', 'surface', 'composition'.
- **Response:**
  - 201 Created: User registration successful.
  - 400 Bad Request: If the user ID already exists.

---

## User Login

- **Endpoint:** `/api/login`
- **Method:** POST
- **Description:** Logs in a user.
- **Content type:** form-data
- **Parameters:**
  - `userID` (string, required): User ID.
  - `userPassword` (string, required): User password.
- **Response:**
  - 200 OK: If login is successful.
  - 401 Unauthorized: If the user ID or password is invalid.

---

## User Logout

- **Endpoint:** `/api/logout`
- **Method:** GET
- **Description:** Logs out the current user.
- **Response:** 200 OK.

---

## Get Orders

- **Endpoint:** `/api/orders`
- **Method:** GET
- **Description:** Retrieves a list of orders.
- **Parameters:**
  - `sort_by` (string, optional): Sorting parameter. Default is `priority`. Allowed values: `priority`, `createdAt`.
- **Response:**
  - 200 OK: List of orders in JSON format.
    - allFilePaths: list of file paths
  
---

## Add Order

- **Endpoint:** `/api/orders`
- **Method:** POST
- **Description:** Adds a new order.
- **Content type:** form-data
- **Parameters:**
  - `priority` (string, required): Priority of the order. Allowed values: 'regular', 'urgent', 'emergency'.
  - `factory` (string, required): Factory where the order is placed. Allowed values: 'Fab A', 'Fab B', 'Fab C'.
  - `lab` (string, required): Laboratory for the order. Allowed values: 'chemical', 'surface', 'composition'.
  - `file` (file, optional): File attachments for the order.
    - Maximum 16 MB for each file.
    - Allowed extensions: txt, pdf, png, jpg, jpeg.
  - `approvedBy` (string, optional): User id to approve the order.
- **Response:**
  - 201 Created: Order creation successful.
  
---

## Get Order by ID

- **Endpoint:** `/api/orders/<int:id>`
- **Method:** GET
- **Description:** Retrieves an order by its ID.
- **Parameters:**
  - `id` (integer, required in url): Serial number of the order.
- **Response:**
  - 200 OK: Order details in JSON format.
  - 404 Not Found: If the order with the specified ID does not exist.

---

## Adjust Order Priority

- **Endpoint:** `/api/orders/<int:id>`
- **Method:** PUT
- **Description:** Adjusts the priority of an order.
- **Content type:** application/json
- **Parameters:**
  - `id` (integer, required in url): Serial number of the order.
  - `priority` (string, required): New priority for the order. Allowed values: 'regular', 'urgent', 'emergency'.
- **Response:**
  - 200 OK: Order priority updated successfully.
  - 400 Bad Request: If the user does not have permission to adjust the order.

---

## Delete Order

- **Endpoint:** `/api/orders/<int:id>`
- **Method:** DELETE
- **Description:** Delete an order.
- **Parameters:**
  - `id` (integer, required in url): Serial number of the order.
- **Response:**
  - 200 OK: Order deleted successfully.
  - 403 Forbidden: If the user is not authorized to delete the order.
---

## Get Orders for Approval

- **Endpoint:** `/api/get_approve_order`
- **Method:** GET
- **Description:** Retrieves a list of orders awaiting approval by the current user.
- **Response:**
  - 200 OK: List of orders in JSON format.

---

## Approve Order

- **Endpoint:** `/api/approve_order/<int:id>`
- **Method:** POST
- **Description:** Approves or rejects an order.
- **Content type:** application/json
- **Parameters:**
  - `id` (integer, required in url): Serial number of the order.
  - JSON body:
    - `action` (string, required): Action to be performed. Allowed values: 'Approve', 'Reject'.
- **Response:**
  - 200 OK: Order updated successfully.
  - 404 Not Found: If the order with the specified ID does not exist.
  - 403 Forbidden: If the user is not authorized to approve the order.

---

## Complete Order

- **Endpoint:** `/api/complete_order/<int:id>`
- **Method:** POST
- **Description:** Marks an order as completed.
- **Parameters:**
  - `id` (integer, required in url): Serial number of the order.
- **Response:**
  - 200 OK: Order updated successfully.
  - 404 Not Found: If the order with the specified ID does not exist.
  - 403 Forbidden: If the user department does not match the order lab or if the order status is not appropriate for completion.

---

## Download file

- **Endpoint:** `/api/download`
- **Method:** POST
- **Description:** Marks an order as completed.
- **Parameters:**
  - `filePath` (string): File path to download.
- **Response:**
  - 200 OK: Content with file.
  - 404 Not Found: If the file does not exist.

---

## Count order

- **Endpoint:** `/api/count_order`
- **Method:** GET
- **Description:** Count the amount of order in each status.
- **Response:**
  - 200 OK: json {status: number}.

---

## Get used space

- **Endpoint:** `/api/used_space`
- **Method:** GET
- **Description:** Get thr used space of the download files folder.
- **Response:**
  - 200 OK: json {used: number (KB)}.