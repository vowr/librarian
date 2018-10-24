<?php
define("DEBUG",'true');
$datetime = new DateTime();
$servername = "localhost";
$username = "radiodj";
$password = "d43ty9z7";
$limit=25;
$start=0;
$logf=fopen('log/Mysearch.log','a+');

  echo "<html>";
  echo "<head>";
  echo "<title> VOWR Music Library </title>";
  echo '<link rel="stylesheet" href="vowr.css">';
  echo "</head>";
// echo '<body>';
// check css 
  echo '<form action="search.php" method="post">';
  echo '<table id="demo-table"; align="center" >';
// echo "<table style='border: solid 1px black'; align='center'; bgcolor='blue';>";
  echo "<caption>Search Library</caption>";
  echo "<tr><th align='left'>Artist</th><th align='left'>Title</th><th align='left'>Albnum</th></tr>";
// echo "<tr><th align='left'>Artist</th><th align='left'>Title</th><th align='left' size=50>Albnum</th><th>Media</th><th>More</th></tr>";
  if ( !$_POST )
  {
    echo '<tr><td><input type="text" name="Artist" size="50"></td>';
    echo '<td><input type="text" name="Title" size="50"></td>';
    echo '<td><input type="text" name="Albnum" size="10"></td>';
    // echo '<td><input type="text" name="Media" size="4"></td>';
    echo '<tr><td><input type="submit" name="Search" value="Search"></td></tr>';
    echo '</table>';
  }
  else
  {
   if ( $_POST["Artist"] )
   {
//     echo " Artist added \n";
     echo '<tr><td><input type="text" name="Artist" size="50" value="'.$_POST["Artist"].'"></td>';
   }
   else
   {
    echo '<tr><td><input type="text" name="Artist" size="50"></td>';
   }
   if ($_POST["Title"] )
   {
     echo '<td><input type="text" name="Title" size="50" value="'.$_POST["Title"].'"></td>';
   }
   else 
   {
     echo '<td><input type="text" name="Title" size="50"></td>';
   }
   if ($_POST["Albnum"] )
   {
     echo '<td><input type="text" name="Albnum" size="10"" value="'.$_POST["Albnum"].'"></td>';
   }
   else
   {
     echo '<td><input type="text" name="Albnum" size="10"></td>';
   }
  /* `if ($_POST["Media"] )
  {
     echo '<td><input type="text" name="Media" size="10"" value="'.$_POST["Media"].'"></td></tr>';
  }
  else
  {
     echo '<td><input type="text" name="Media" size="10"></td></tr>';
  } */
  echo '<tr><td><input type="submit" name="Search" value="Search"></td></tr>';
  echo '</table>';
	 // If ( $_POST["Search"] == "Search" ) 
	 If ( $_POST["Search"] ) 
	 {
	        $start = 0;
                echo ' <input type="hidden" name="More" value="'.$limit.'">';
	 }
         else
         {
          if ($_POST["More"] >= 0)
          {
	     $start = $_POST["More"];
 // echo " </p> Start is = ".$start;
	     $start = $_POST["More"] + $limit;
	      // $start = $_POST["More"];
	    $_POST["More"] += $limit;
// echo "</p>  Start is 2 = ".$start;
//    echo "starting in post More = ".$_POST["More"];
//    echo " Submit = " . $_POST["Search"] ."</p>";
		echo '<input type="hidden" name="More" value="'.$_POST["More"].'">';
         }
         else 
         {
	       // $start = 0;
    echo "</p> Starting ".$start;
               echo ' <input type="hidden" name="More" value="'.$limit.'">';
               //  echo ' <td><input type="text" name="More" size="3" value="'.$limit.'"></td>';
         }
         }
}
// Output table
  echo '<table id="demo_table": style="border: solid 1px black;" align="center">';
  echo "<tr><th>Artist</th><th>Title</th><th>Albnum</th><th>Track</th><th>Side</th><th>Media</th><th>Category</th><th>Can</th></tr>";

class TableRows extends RecursiveIteratorIterator {
    function __construct($it) {
        parent::__construct($it, self::LEAVES_ONLY);
    }

    function current() {
        // return "<td style='width:150px;border:1px solid black;'>" . parent::current(). "</td>";
// 	    echo parent::current();
	$red=0;
	    if (parent::current() == "Y") { 
                return '<td bgcolor="#ff00ff" style="border:1px solid black;">' . parent::current(). "</td>";
	    }
	    else 
		{
        return "<td style='border:1px solid black;'>" . parent::current(). "</td>";
		}
        // return "<td>" . parent::current(). "</td>";
    }

    function beginChildren() {
	    if ( parent::current() == "Y" ) { echo '<tr bgcolor="#ff0000">'; }
	    else { echo "<tr>"; }
    }

    function endChildren() {
        // echo "</tr>" . "\n";
        echo "</tr>";
    }
  } 

// $stmt= "SELECT mcategory,artist, title,albnum,track,side, media FROM music ";
  $stmt= "SELECT  artist,title,albnum,track,side, media,mcategory,canadian FROM music ";
  $cnt = "select count(1) from music "; 
 // echo "<p>".$stmt."</p>";
  if ( $_POST )
  {
//  echo "POST active";
 // $where=0;
	// echo "adding where statement";
    $where="";
    if ( $_POST["Artist"] )
    {
// echo " Artist added \n";
       $str=strtolower($_POST["Artist"]);
       $where .= " where lower(artist) like concat('%',:A,'%') ";
    }
    if ($_POST["Title"] )
     {
      $str1=strtolower($_POST["Title"]);
      if (!$where) { $where .= " where lower(title) like concat('%',:T,'%') "; }
      else { $where .= " and lower(title) like concat('%',:T,'%')"; }
     }
    if ($_POST["Albnum"] )
     {
      $str3=strtolower($_POST["Albnum"]);
      if (!$where) { $where .= " where lower(albnum) like concat('%',:N,'%') "; }
      else { $where .= " and lower(albnum) like concat('%',:N,'%')"; }
     }
   $stmt .= $where; 
   $cnt .= $where;
  }
  $stmt = $stmt." order  by artist,albnum, side, track";
  $stmt = $stmt." limit ".$start.",". $limit;
      try {
       $conn = new PDO("mysql:host=$servername;dbname=radiodj", $username, $password);
     // set the PDO error mode to exception
       $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
     // echo "Connected successfully";
       fwrite($logf, $datetime->format('Y-M-D H:i:s').'conected succesfully'.PHP_EOL);
     }
       	catch(PDOException $e) {
         echo "Connection failed: " . $e->getMessage();
         fwrite($logf, $datetime->format('Y-M-D H:i:s').'login failed error code:' . $e->getMessage().PHP_EOL);
        }
   $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
   $stmtp = $conn->prepare($stmt);
   $cntp = $conn->prepare($cnt);
//  BINDING
// Bind the variables
//
   if ( $_POST )
   {
 // echo "Post recieved";
     if ( $_POST["Artist"] )
     {
	   try {
            $stmtp->bindParam(':A', $str, PDO::PARAM_STR, 50);
            $cntp->bindParam(':A', $str, PDO::PARAM_STR, 50);
	   }
       	    catch(PDOException $e) {
            echo " Bind failed: " . $e->getMessage();
            isset($e) && DEBUG ? $e='' : fwrite(logf, " Bind error: ",$e[message].PHP_EOL);
           }
     }
      if ($_POST["Title"] )
      {
	   Try {
            $stmtp->bindParam(':T', $str1, PDO::PARAM_STR, 100);
            $cntp->bindParam(':T', $str1, PDO::PARAM_STR, 100);
	   }
       	    catch(PDOException $e) {
            isset($e) && DEBUG ? $e='' : fwrite(logf, " Bind1 error: ",$e[message].PHP_EOL);
            }
      }
      if ($_POST["Albnum"] )
      {
	   Try {
            $stmtp->bindParam(':N', $str3, PDO::PARAM_STR, 50);
            $cntp->bindParam(':N', $str3, PDO::PARAM_STR, 50);
	   }
           catch(PDOException $e) {
           isset($e) && DEBUG ? $e='' : fwrite(logf, " Bind3 error: ",$e[message].PHP_EOL);
	  }
   }
  }
   // BINDING
//  echo "<p>".$stmt."</p>";
    $stmtp->execute();
    $cntp->execute();
// set the resulting array to associative
    $result = $stmtp->setFetchMode(PDO::FETCH_ASSOC);
    $count = $cntp->setFetchMode(PDO::FETCH_NUM);
    $total = $cntp->fetch();
    $page = $limit + $start;
      if ( $total[0] > $page)
      {
// echo "</p>total songs found = ".$total[0]. " Start = ". $start;
              echo '<input type="hidden" name="More" value="'.$start.'">';
              echo '<tr><td><input type="submit" value="Next"></td>';
	      echo '<td> Songs '.$start.' to '.$page.' of '.$total[0].' songs </td></tr>'; 
      } 

 // echo "<p>".$result. " result </p>";
// echo $count. " count</p> ";
      foreach(new TableRows(new RecursiveArrayIterator($stmtp->fetchAll())) as $k=>$v) 
      {
        echo $v;
      }
//    echo $stmt; 
  echo "</table>";
  echo " </form>";
  echo "</html>";
  $conn = null;
// echo "Exiting</p>";
?>
