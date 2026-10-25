
<?php

require_once __DIR__ . "/../config/database.php";

$usuario = trim($_POST["usuario"] ?? "");
$senha = $_POST["senha"] ?? "";

if ($usuario == "" || $senha == "") {
    exit("Preencha todos os campos!");
}

$senhaCriptografada = password_hash($senha, PASSWORD_DEFAULT);

try {
    $sql = $pdo->prepare(
        "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)"
    );

    $sql->execute([$usuario, $senhaCriptografada]);

    echo "Cadastro realizado com sucesso!";

} catch (PDOException $e) {
    // Mostrar erro apenas durante testes locais
    echo "Erro no cadastro: " . $e->getMessage();
}

?>
