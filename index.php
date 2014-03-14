<html lang="en-us">
<head>
<meta http-equiv="Content-Type" content="text/html" charset="utf-8"/>
<link rel="shortcut icon" href="./assets/images/nikolas-favicon.png">

<title>Logve</title>
</head>
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-35727252-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
<body>
    <div id="about-me">
            <form action="upload_file.php" method="post" enctype="multipart/form-data">
                    History File: <input type="file" name="file" id="file"><br>
                    <input type="submit" name="submit" value="Upload!">
            </form>
            <?php echo ini_get("disable_functions");?>

    </div>
</body>
</script>
</html>