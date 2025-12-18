#!/usr/bin/env python3
"""
Calculateur d'adresses réseau et broadcast.
Permet de calculer l'adresse réseau et broadcast à partir d'une IP et d'un masque.
"""

import sys
import re


def valider_ip(ip: str) -> bool:
    """Valide qu'une adresse IP est correcte."""
    parties = ip.split('.')
    if len(parties) != 4:
        return False
    for partie in parties:
        try:
            valeur = int(partie)
            if valeur < 0 or valeur > 255:
                return False
        except ValueError:
            return False
    return True


def valider_masque(masque: str) -> bool:
    """Valide qu'un masque est correct (format décimal ou CIDR)."""
    # Format CIDR (ex: 26)
    if masque.isdigit():
        cidr = int(masque)
        return 0 <= cidr <= 32
    # Format décimal (ex: 255.255.255.192)
    return valider_ip(masque)


def cidr_vers_masque(cidr: int) -> str:
    """Convertit un masque CIDR en format décimal pointé."""
    masque_binaire = '1' * cidr + '0' * (32 - cidr)
    octets = [int(masque_binaire[i:i+8], 2) for i in range(0, 32, 8)]
    return '.'.join(map(str, octets))


def ip_vers_binaire(ip: str) -> str:
    """Convertit une adresse IP en format binaire pointé."""
    octets = ip.split('.')
    binaire = [format(int(octet), '08b') for octet in octets]
    return '.'.join(binaire)


def binaire_vers_ip(binaire: str) -> str:
    """Convertit une adresse binaire pointée en format décimal."""
    octets = binaire.split('.')
    decimal = [str(int(octet, 2)) for octet in octets]
    return '.'.join(decimal)


def calculer_adresse_reseau(ip_binaire: str, masque_binaire: str) -> str:
    """Calcule l'adresse réseau avec un ET logique entre IP et masque."""
    # Supprimer les points pour le calcul
    ip_bits = ip_binaire.replace('.', '')
    masque_bits = masque_binaire.replace('.', '')
    
    # ET logique bit à bit
    reseau_bits = ''.join(
        '1' if ip_bits[i] == '1' and masque_bits[i] == '1' else '0'
        for i in range(32)
    )
    
    # Reformater avec les points
    return '.'.join(reseau_bits[i:i+8] for i in range(0, 32, 8))


def calculer_adresse_broadcast(ip_binaire: str, masque_binaire: str) -> str:
    """Calcule l'adresse broadcast avec un OU logique entre IP et l'inverse du masque."""
    # Supprimer les points pour le calcul
    ip_bits = ip_binaire.replace('.', '')
    masque_bits = masque_binaire.replace('.', '')
    
    # Inverser le masque
    masque_inverse = ''.join('0' if bit == '1' else '1' for bit in masque_bits)
    
    # OU logique bit à bit
    broadcast_bits = ''.join(
        '1' if ip_bits[i] == '1' or masque_inverse[i] == '1' else '0'
        for i in range(32)
    )
    
    # Reformater avec les points
    return '.'.join(broadcast_bits[i:i+8] for i in range(0, 32, 8))


def parser_entree(entree: str) -> tuple[str, str]:
    """Parse l'entrée au format IP/CIDR ou IP masque."""
    entree = entree.strip()
    
    # Format CIDR (ex: 192.168.1.150/26)
    if '/' in entree:
        parties = entree.split('/')
        if len(parties) != 2:
            raise ValueError("Format invalide. Utilisez IP/CIDR (ex: 192.168.1.150/26)")
        ip, masque = parties[0], parties[1]
        
        if not valider_ip(ip):
            raise ValueError(f"Adresse IP invalide: {ip}")
        
        if masque.isdigit():
            cidr = int(masque)
            if not (0 <= cidr <= 32):
                raise ValueError(f"CIDR invalide: {masque} (doit être entre 0 et 32)")
            masque = cidr_vers_masque(cidr)
        elif not valider_ip(masque):
            raise ValueError(f"Masque invalide: {masque}")
        
        return ip, masque
    
    # Format avec espace (ex: 192.168.1.150 255.255.255.192)
    parties = entree.split()
    if len(parties) == 2:
        ip, masque = parties
        if not valider_ip(ip):
            raise ValueError(f"Adresse IP invalide: {ip}")
        if masque.isdigit():
            cidr = int(masque)
            if not (0 <= cidr <= 32):
                raise ValueError(f"CIDR invalide: {masque}")
            masque = cidr_vers_masque(cidr)
        elif not valider_ip(masque):
            raise ValueError(f"Masque invalide: {masque}")
        return ip, masque
    
    raise ValueError("Format invalide. Utilisez IP/CIDR ou IP MASQUE")


def afficher_recap(ip: str, masque: str) -> None:
    """Affiche le récapitulatif des calculs."""
    # Conversions en binaire
    ip_binaire = ip_vers_binaire(ip)
    masque_binaire = ip_vers_binaire(masque)
    
    # Calculs
    reseau_binaire = calculer_adresse_reseau(ip_binaire, masque_binaire)
    broadcast_binaire = calculer_adresse_broadcast(ip_binaire, masque_binaire)
    
    # Conversions en décimal
    reseau_decimal = binaire_vers_ip(reseau_binaire)
    broadcast_decimal = binaire_vers_ip(broadcast_binaire)
    
    # Affichage
    print("\n" + "=" * 60)
    print("CALCULATEUR D'ADRESSES RÉSEAU ET BROADCAST")
    print("=" * 60)
    
    print("\n📋 Représentation binaire:")
    print("-" * 60)
    print(f"@IP {ip_binaire}")
    print(f"@M  {masque_binaire}")
    print(f"@R  {reseau_binaire}")
    print(f"@B  {broadcast_binaire}")
    
    print("\n📋 Résultats en décimal:")
    print("-" * 60)
    print(f"Adresse IP      : {ip}")
    print(f"Masque          : {masque}")
    print(f"Adresse Réseau  : {reseau_decimal}")
    print(f"Adresse Broadcast: {broadcast_decimal}")
    print("=" * 60 + "\n")


def main():
    """Fonction principale."""
    print("\n🖥️  Calculateur d'adresses réseau et broadcast")
    print("-" * 45)
    
    if len(sys.argv) > 1:
        # Mode ligne de commande
        entree = ' '.join(sys.argv[1:])
    else:
        # Mode interactif
        print("Entrez l'adresse IP et le masque")
        print("Formats acceptés:")
        print("  - IP/CIDR (ex: 192.168.1.150/26)")
        print("  - IP MASQUE (ex: 192.168.1.150 255.255.255.192)")
        print()
        entree = input("Votre entrée: ")
    
    try:
        ip, masque = parser_entree(entree)
        afficher_recap(ip, masque)
    except ValueError as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
