<html>
<head>
<title>My First HTML web page</title>
<?php
echo $_GET["name"];
?>
</head>
<body>
<FORM name="form1" action="firstexample.php" method="GET">
Name : <input type="text" name="namingModel"><br>
Business : <input type="text" name="filename"><br>
Overcast : <input type="text" name="Overcast"><br>
Temp : <input type="text" name="Temp"><br>
Wind : <input type="text" name="Wind"><br>
Precipitation : <input type="text" name="Precipitation"><br>
MLAlgorithms : <input type="text" name="MLAlgorithms"><br>
Hyperparams :<input type="text" id="learnRate"><br>
Hyperparams :<input type="text" id="maxDepth"><br>
Hyperparams :<input type="text" id="dataSetSplit"><br>
Hyperparams :<input type="text" id="myRange"><br>

<input type="submit" name="Submit1" value="Login">
</FORM>
</body>
</html>
