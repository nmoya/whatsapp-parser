<?php

if ($_FILES["file"]["error"] > 0)
  {
  echo "Error: " . $_FILES["file"]["error"] . "<br>";
  }
else
  {
  echo "Upload: " . $_FILES["file"]["name"] . "<br>";
  echo "Type: " . $_FILES["file"]["type"] . "<br>";
  echo "Size: " . ($_FILES["file"]["size"] / 1024) . " kB<br>";
  move_uploaded_file($_FILES["file"]["tmp_name"], "uploads/" . $_FILES["file"]["name"]);
  echo "Stored in: " . $_FILES["file"]["tmp_name"];
  echo "python main.py uploads/" . $_FILES["file"]["name"] . " > output.txt";
  echo exec("python main.py uploads/" . $_FILES["file"]["name"] . " > output.txt");
  header("Location: http://beeway-stanze.codio.io:3000/output.txt");
  }

?>