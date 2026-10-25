
<?php

$acao = $_GET["acao"] ?? "";

if ($acao == "Entrar") {
    header("Location: Pagina%20login/TelaLogin.html");
    exit;
}

elseif ($acao == "Cadastrar") {
    header("Location: Tela%20Cadastro/TelaCadastro.html");
    exit;
}

?>