
<?php

session_start();

require_once __DIR__ . "/../config/database.php";

$usuario = $_POST["usuario"] ?? "";
$senha = $_POST["senha"] ?? "";

if ($usuario == "" || $senha == "") {
    exit("Preencha todos os campos!");
}

$sql = $pdo->prepare(
    "SELECT USU_ID, USUARIO, SENHA
     FROM usuarios
     WHERE USUARIO = ?"
);

$sql->execute([$usuario]);

$conta = $sql->fetch();

if ($conta && password_verify($senha, $conta["SENHA"])) {

    session_regenerate_id(true);

    $_SESSION["id"] = $conta["USU_ID"];
    $_SESSION["usuario"] = $conta["USUARIO"];

    header("Location: ../view.html");
    exit;

} else {
    echo "Usuário ou senha incorretos!";
}

?>
