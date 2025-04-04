# O/a candidato/a deverá desenvolver um programa na linguagem de sua preferência (Java, C# ou outra) que lerá arquivos de texto com XML formatados e realizar operações correspondentes em uma base LDAP (OpenDJ, Open LDAP, eDirectory, Active Directory ou outra).

# Condições para o desenvolvimento:
    # Para trabalhar com o XML, deverá ser utilizado o XPath ou similar;
    # As classes e atributos deverão ser os nativos da ferramenta LDAP escolhida;
    # Campos relacionados a nome e login deverão ter apenas texto e o telefone apenas números (utilizar expressão regular);
    # Usuários e grupos deverão estar em containers distintos.

# O/a candidato/a deverá apresentar a funcionalidade construída e será avaliada a lógica construída e o domínio dos dados. 

import re
import xml.etree.ElementTree as ET
from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_DELETE

LDAP_SERVER = "ldap://localhost:10389"  
LDAP_USER = "uid=admin,ou=system"
LDAP_PASSWORD = "secret"
BASE_DN_USERS = "ou=users,dc=example,dc=com"
BASE_DN_GROUPS = "ou=groups,dc=example,dc=com"

REGEX_TEXTO = re.compile(r'^[A-Za-z\s]+$')  
REGEX_TELEFONE = re.compile(r'^\d+$')  

def validar_dados(nome, login, telefone):
    if not REGEX_TEXTO.match(nome):
        raise ValueError(f"Nome inválido: {nome}")
    if not REGEX_TEXTO.match(login):
        raise ValueError(f"Login inválido: {login}")
    if not REGEX_TELEFONE.match(telefone):
        raise ValueError(f"Telefone inválido: {telefone}")

def conectar_ldap():
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, LDAP_USER, LDAP_PASSWORD, auto_bind=True)
    return conn

def adicionar_usuario(conn, nome, login, telefone):
    dn = f"cn={login},{BASE_DN_USERS}"
    atributos = {
        'objectClass': ['inetOrgPerson', 'top'],
        'cn': nome,
        'sn': login,
        'uid': login,
        'telephoneNumber': telefone,
        'userPassword': 'SenhaSegura123'
    }
    conn.add(dn, attributes=atributos)
    print(f"Usuário {login} adicionado ao ApacheDS.")

def adicionar_grupo(conn, grupo, membros):
    dn = f"cn={grupo},{BASE_DN_GROUPS}"
    atributos = {
        'objectClass': ['groupOfNames', 'top'],
        'cn': grupo,
        'member': [f"cn={membro},{BASE_DN_USERS}" for membro in membros]
    }
    conn.add(dn, attributes=atributos)
    print(f"Grupo {grupo} criado com membros {membros}.")

def processar_xml(arquivo_xml):
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()
    conn = conectar_ldap()

    for usuario in root.findall(".//add[@class-name='Usuario']"):
        if usuario is not None:
            nome = usuario.find(".//add-attr[@attr-name='Nome Completo']/value").text.strip()
            login = usuario.find(".//add-attr[@attr-name='Login']/value").text.strip()
            telefone = usuario.find(".//add-attr[@attr-name='Telefone']/value").text.strip()
            grupos = [g.text.strip() for g in usuario.findall(".//add-attr[@attr-name='Grupo']/value")]
            
            print(f"Usuário encontrado: {nome}, Login: {login}, Telefone: {telefone}, Grupos: {grupos}")
            adicionar_usuario(conn, nome, login, telefone, grupos)
        else:
            print("Nenhum usuário encontrado no XML.")

    for grupo in root.findall(".//add[@class-name='Grupo']"):
        identificador = grupo.find(".//add-attr[@attr-name='Identificador']/value").text.strip()
        descricao = grupo.find(".//add-attr[@attr-name='Descricao']/value").text.strip()
        adicionar_grupo(conn, identificador, descricao)
        
    conn.unbind()
    print("Processamento concluído.")

def modificar_usuario(conn, login, remover_grupos, adicionar_grupos):
    """Modifica os grupos de um usuário no ApacheDS."""
    dn_usuario = f"cn={login},{BASE_DN_USERS}"
    
    for grupo in remover_grupos:
        dn_grupo = f"cn={grupo},{BASE_DN_GROUPS}"
        conn.modify(dn_grupo, {'member': [(MODIFY_DELETE, [dn_usuario])]})
        print(f"Usuário {login} removido do grupo {grupo}.")
    
    for grupo in adicionar_grupos:
        dn_grupo = f"cn={grupo},{BASE_DN_GROUPS}"
        conn.modify(dn_grupo, {'member': [(MODIFY_ADD, [dn_usuario])]})
        print(f"Usuário {login} adicionado ao grupo {grupo}.")

def processar_xml_modificacao(arquivo_xml):
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()
    conn = conectar_ldap()
    
    usuario = root.find(".//modify[@class-name='Usuario']")
    if usuario is not None:
        login = usuario.find(".//association").text.strip()
        remover_grupos = [g.text.strip() for g in usuario.findall(".//modify-attr[@attr-name='Grupo']/remove-value/value")]
        adicionar_grupos = [g.text.strip() for g in usuario.findall(".//modify-attr[@attr-name='Grupo']/add-value/value")]
        
        print(f"Modificando usuário: {login}")
        print(f"Removendo dos grupos: {remover_grupos}")
        print(f"Adicionando aos grupos: {adicionar_grupos}")
        modificar_usuario(conn, login, remover_grupos, adicionar_grupos)
    else:
        print("Nenhum usuário encontrado no XML de modificação.")
    
    conn.unbind()
    print("Processamento de modificação concluído.")

def main():
    processar_xml("AddGrupo1.xml")
    processar_xml("AddGrupo2.xml")
    processar_xml("AddGrupo3.xml")
    processar_xml("AddUsuario1.xml")
    processar_xml_modificacao("ModifyUsuario")
    

if __name__ == "__main__":
    main()
