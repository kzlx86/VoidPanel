
<?php

$host = "127.0.0.1";
$porta = 3306; // MySQL80 separado
$banco = "VoidPanel";
$usuario = "root";
$senha = "310709Banco#";

try {
    $pdo = new PDO(
        "mysql:host=$host;port=$porta;dbname=$banco;charset=utf8mb4",
        $usuario,
        $senha,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]
    );
} catch (PDOException $e) {
    error_log($e->getMessage());
    exit("Não foi possível conectar ao banco de dados.");
}
