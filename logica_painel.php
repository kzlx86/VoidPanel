<?php

// Session_start serve para o 
$usuario = $_POST["usuario"];
$senha = $_POST["senha"];

if ($_SERVER["REQUESTED_METHOD"] === "POST"){
    $usuario = $_POST["usuario"] ?? "";
    $senha = $_POST["senha"] ?? "";
    if ($usuario === "admin" && $senha === "1234") {

        //O session_regenerate_id serve para criar um id para cada usuário!
        session_regenerate_id(true);

        $_SESSION["logado"] = true;
        $_SESSION["usuario"] = $usuario

        // O header serve para mandar o usuario para outra pagina port exemplo
        header("Location: painel.html")
    } else {
        echo "Usuário ou senha inválidos.";
    }
}

?>