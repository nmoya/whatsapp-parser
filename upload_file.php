<?php

        if ($_FILES["file"]["error"] > 0)
            echo "Error: " . $_FILES["file"]["error"] . "<br>";
        else
        {
            echo "Upload: " . $_FILES["file"]["name"] . "<br>";
            echo "Type: " . $_FILES["file"]["type"] . "<br>";
            echo "Size: " . ($_FILES["file"]["size"] / 1024) . " kB<br>";
            echo "Temp name: ". $_FILES["file"]["tmp_name"] . "<br>";
            move_uploaded_file($_FILES["file"]["tmp_name"], "./uploads/" . $_FILES["file"]["name"]);
            echo "python main.py uploads/" . $_FILES["file"]["name"]."<br>";
            $json = escapeshellcmd(passthru("python main.py uploads/" . $_FILES["file"]["name"]));

            //header("Location: http://beeway-stanze.codio.io:3000/output.txt");
        }
?>