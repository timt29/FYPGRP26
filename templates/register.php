<?php
session_start();
require 'db.php';

$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name']);
    $email = trim($_POST['email']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];

    if (empty($name) || empty($email) || empty($password) || empty($confirm_password)) {
        $errors[] = "Please fill in all required fields.";
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Invalid email format.";
    }

    if ($password !== $confirm_password) {
        $errors[] = "Passwords do not match.";
    }

    /*if (empty($errors)) {
        // Check if email exists
        $stmt = $pdo->prepare("SELECT user_id FROM users WHERE email = ?");
        $stmt->execute([$email]);

        if ($stmt->fetch()) {
            $errors[] = "Email already registered.";
        } else {
            $stmt = $pdo->prepare("INSERT INTO users (name, phone, email, password, type) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([$name, $phone, $email, $password, $type]);
            $_SESSION['success'] = "Registration successful. You may now login.";
            header("Location: login.php");
            exit();
        }
    }*/
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Register</title>
<link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="login-container">
    <h2>Register</h2>

    <?php if (!empty($errors)): ?>
      <div class="error-message">
        <ul>
          <?php foreach ($errors as $err): ?>
            <li><?= htmlspecialchars($err) ?></li>
          <?php endforeach; ?>
        </ul>
      </div>
    <?php endif; ?>

    <form method="post" action="register.php" novalidate>
      <label for="name">Name*</label>
      <input type="text" id="name" name="name" required value="<?= htmlspecialchars($_POST['name'] ?? '') ?>">

      <label for="email">Email*</label>
      <input type="email" id="email" name="email" required value="<?= htmlspecialchars($_POST['email'] ?? '') ?>">

      <label for="password">Password*</label>
      <input type="password" id="password" name="password" required>

      <label for="confirm_password">Confirm Password*</label>
      <input type="password" id="confirm_password" name="confirm_password" required>

      <button type="submit" style="margin-top:20px;">Register</button>
    </form>

    <p class="register-link">Already registered? <a href="login.php">Login here</a>.</p>
  </div>
</body>
</html>

