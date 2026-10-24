<?php

$acao = $_GET["acao"]

if($acao == "Entrar"){
    header("Location: LogicaLogin.php")
    exit;
}

elseif($acao == Cadastrar){
    header("Location: LogicaCadastro.php")
}

?>