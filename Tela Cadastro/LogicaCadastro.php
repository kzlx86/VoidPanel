<?php
require "Conexao.php";

$usuario = $_POST["usuario"] ?? "";
$senha = $_POST["senha"] ?? "";

if ($usuario == "" || $senha == "") {
    exit("Preencha todos os campos!");
}

$senha = password_hash($senha, PASSWORD_DEFAULT);

$sql = $conexao->prepare(
    "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)"
);

$sql->bind_param("ss", $usuario, $senha);

if ($sql->execute()) {
    echo "Cadastro realizado com sucesso!";
} else {
    echo "Não foi possível cadastrar. O usuário já existi.";
}
?>