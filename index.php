<?php
#define("TOKEN", "put token here or take from \$_ENV");
define("TOKEN", "put toekn here or take from \$_ENV");

function response(){
    return 'BAD REQUEST';
}

function isValidJSON($str){
    json_decode($str);
    return json_last_error() == JSON_ERROR_NONE;
}

function read_hash($base){
    $file_path = "$base/api/v1/state.json";
    if(is_file($file_path)){
        $file = fopen($file_path,'r');
        $data = fread($file,filesize($file_path));
        fclose($file);
        if(isValidJSON($data)){
            $data_json = json_decode($data,true);
            return $data_json['data'];
        }
        return $data;
    }
    return '';
}

$base = "$_SERVER[DOCUMENT_ROOT]/covid";

if($_SERVER['REQUEST_METHOD']==='POST'){
    if(isset($_SERVER['HTTP_TOKEN'])){
        if(isset($_SERVER['HTTP_JSON_NAME']) && isset($_SERVER['HTTP_JSON_PATH'])){
            if($_SERVER['HTTP_TOKEN']===TOKEN){
                $data = file_get_contents('php://input');
                $path = "$base$_SERVER[HTTP_JSON_PATH]";
                if(is_dir($path)===false){
                    mkdir($path,0,true);
                }
                $file = fopen("$path/$_SERVER[HTTP_JSON_NAME]",'w');
                fwrite($file, $data);
                fclose($file);
            }else{
                #echo response();
                echo "BAD token";
            }
        }elseif(isset($_SERVER['HTTP_DATA_HASH'])){
            $data_hash = read_hash($base);
            if($data_hash===$_SERVER['HTTP_DATA_HASH']){
                echo '{"update":false}';
            }
            else{
                echo '{"update":true}';
            }
        }
    }else{
        #echo response();
        echo "BAD headers";
    }
}else{
    echo response();
}
?>