<?php
session_start();
require "Conexao.php";

$usuario = $_POST["usuario"] ?? "";
$senha = $_POST["senha"] ?? "";

$sql = $conexao->prepare(
    "SELECT id, usuario, senha FROM usuarios WHERE usuario = ?"
);

$sql->bind_param("s", $usuario);
$sql->execute();

$resultado = $sql->get_result();
$conta = $resultado->fetch_assoc();

if ($conta && password_verify($senha, $conta["senha"])) {
    session_regenerate_id(true);

    $_SESSION["id"] = $conta["id"];
    $_SESSION["usuario"] = $conta["usuario"];

    header("Location: Painel.php");
    exit;
} else {
    echo "Usuário ou senha incorretos!";
}
?>