#! /usr/bin/env python3

#########################################################################################
# -Autor: Carlos Moro Jiménez
# -Versión: 0.0
#########################################################################################
# la linea de arriba sirve solo para Linux

# Páginas de consulta:

"""
Mirar que es cada etiqueta: http://help.mp3tag.de/main_tags.html
"""


import argparse
import textwrap
import os
import re
from pathlib import Path
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError
from mutagen.easymp4 import EasyMP4, EasyMP4Tags


class mp3Tag():

    """ TODO-Permitir seleccionar que quieres taggear.
        TODO-Taggear una canción en particular como quieras.
    """

    def manejar_parametros(self):
        ayudaOrdPorJerarquia= textwrap.dedent('''\
        Ordenar por Jerarquía de directorios(los metadatos que sirven para la música del móvil)
        Este programa puede funcionar de forma recursiva. Si deseas que alguna carpeta no sea modificada.
        colocar un archivo sin extensiones de nombre [NOT_DO] Sin los corchetes.
        Detalle:
        Este programa taggea de forma automática tus canciones. Según una estructura fija.
        Resumen: Tagea las canciones según la estructura de directorios:
             Título= nombre del fichero
             Álbum=carpeta en la que se encuentra.
             Interprete=carpeta superior a la actual.

             Ejemplo:
             /- Musica
                      -Discografia talco
                                        -2001 Talco
                                                    -Track1
                                                    -track2
                                                    -...
              ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
             Track1.
             Título=Track1
             Álbum=2001 Talco
             Intérprete=Discografía talco           
        ''')
        parser = argparse.ArgumentParser(description="Modifico tags de música.",formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-OJD", "-Ordenar-porJerarquiaDirectorios", action='store_true', help=ayudaOrdPorJerarquia)
        # Grupo de opciones
        group = parser.add_mutually_exclusive_group()
        sinpreguntas="no pregunta, si quieres modificar solo un parametro.Asume que se quiere modificar todo."
        group.add_argument("-f","--sinPreguntas", action='store_true', help=sinpreguntas)
        global args
        args = parser.parse_args()

    def main(self):
        self.manejar_parametros()
        global args
        if args.OJD:
            print("Hola Usuario")
            if args.sinPreguntas:
                rutaInicio = input("¿En qué directorio vamos a trabajar?.\n Introduce la ruta:")
                self.rename_by_dir_hierarchy(rutaInicio)
            else:  # Por hacer
                print("sin hacer. Solo funciona con opción -f")
                return
                self.menu_rename_by_dir()
                rutaInicio = input("¿En qué directorio vamos a trabajar?.\n Introduce la ruta:")
                self.rename_by_dir_hierarchy(rutaInicio)
        else:
            print("Introduce algún parámetro.")


    """
    Resumen: Tagea las canciones según la estructura de directorios:
             Título= nombre del fichero
             Álbum=carpeta en la que se encuentra.
             Interprete=carpeta superior a la actual.

             Ejemplo
             /- Musica
                      -Discografia talco
                                        -2001 Talco
                                                    -Track1
                                                    -track2
                                                    -...
              ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
             Track1.
             Título=Track1
             Álbum=2001 Talco
             Intérprete=Discografía talco    
    """
    def rename_by_dir_hierarchy(self, ruta_canciones):
        recursivo = input("Desea que la operacion sea recursiva?(afecta a directorios de directorios)(True/False):")
        if recursivo == "True":
            recursivo = True
        else:
            recursivo = False

        self.ruta = Path(ruta_canciones)
        if not self.ruta.exists():
            print("Esa ruta no es válida.")
        try:
            if not self.ruta.is_dir():
                print("Esto no es un directorio.")
                return
            if self.puedo_hacer(self.ruta) is False:
                return
            for fichero in self.ruta.iterdir():  # Este for recorre el directorio de ruta
                # Obtenemos los nombres del directorio padre, directorio actual y fichero.
                # Seran los respectivos nombres de artista,album,titulo respectivamente
                parDir = os.path.basename(os.path.dirname(os.path.normpath(str(self.ruta))))
                directorio = os.path.basename(str(self.ruta))
                name_cancion = os.path.basename(str(fichero))
                # Si opcion recursivo activa y  fichero es un directorio llamar a la función de forma recursiva
                # con la opcion recursivo y de ruta el directorio.
                if fichero.is_dir() and recursivo is True:
                    self.rename_by_dir_hierarchy(str(fichero), recursivo)
                self.add_tag_mp3(fichero, name_cancion, parDir, directorio)
                self.add_tag_flac(fichero, name_cancion, parDir, directorio)
                self.add_tag_m4a(fichero, name_cancion, parDir, directorio)

        except (FileNotFoundError,FileExistsError):
            print("El directorio no existe o no es una dirección válida")
            return

        return print("Operación realizada con aparente éxito.")

    def puedo_hacer(self, ruta):
        for buscoRestriccion in ruta.iterdir():  # recorre la ruta para comprobar que puedo actual.
            if os.path.basename(str(buscoRestriccion)) == "NOT_DO":
                return False
        return True

    def menu_rename_by_dir(self):
        valido=False
        while not valido:
            print("Selecciona una opción: Se cambiarán los tag según escojas")
            print("\n\t1->Activa\n\t0->Desactiva \n(Coloca un 1 o un 0)\nPor ej 010 activa solo álbum.")
            activate_opciones=input("Activar (Título,Álbum,Intérprete):")
            if len(activate_opciones)!=3:
                print("error vuelve a intentarlo.")
            activate_titulo = activate_opciones[0]
            activate_album = activate_opciones[1]
            activate_interprete = activate_opciones[2]
            if (not activate_titulo in (0, 1)):
                print("Debes seleccionar 1 o 0. \nNo se aceptan otras opciones.")
                continue
            activate_album=input("Activar función Álbum:")
            if (not activate_album in (0, 1)):
                print("Debes seleccionar 1 o 0. \nNo se aceptan otras opciones.")
                continue
            activate_interprete=input("Activar función Intérprete:")
            if (not activate_interprete in (0, 1)):
                print("Debes seleccionar 1 o 0. \nNo se aceptan otras opciones.")
                continue
            print("----------------------------------------------------------------------------------------------------")
            valido=True
        return(activate_titulo,activate_album,activate_interprete)

    def add_tag_mp3(self, fichero, name_cancion, parDir, directorio):

        patronMusicaMP3 = re.compile('.\.mp3')  # Utilizaremos el patros para seleccionar archivos mp3
        if patronMusicaMP3.search(str(fichero)):  # Comprobamos si supuestamente es un fich mp3
            name_cancion = name_cancion.rstrip(".mp3")  # ahora al nombre le quitamos la extension que queda fea.
            try:
                print("file", os.path.basename(str(fichero)), "directory_1", os.path.basename(str(self.ruta)), "dir_2:",
                      os.path.basename(os.path.dirname(os.path.normpath(str(self.ruta)))))

                audioTag = EasyID3(str(fichero))
                audioTag['title'] = name_cancion
                audioTag['artist'] = parDir
                audioTag['album'] = directorio
                audioTag['composer'] = ""
                EasyID3.RegisterTextKey("album_artist", "TPE2")
                audioTag['album_artist'] = ""
                print(audioTag['title'], "nuevo")
                audioTag.save(v2_version=3)
                audioTag.save()
            except ID3NoHeaderError:
                audioTag = mutagen.File(str(fichero), easy=True)
                audioTag.add_tags()
                audioTag['title'] = name_cancion
                audioTag['album'] = directorio
                audioTag['artist'] = parDir
                print("No existe un tag previo")
                audioTag.save(v2_version=3)
                audioTag.save()

    def add_tag_flac(self, fichero, name_cancion, parDir, directorio):
        patronMusicaFlac = re.compile('.\.flac')
        if patronMusicaFlac.search(str(fichero)):
            name_cancion = name_cancion.rstrip(".flac")  # ahora al nombre le quitamos la extension que queda fea.
            try:
                print("file", os.path.basename(str(fichero)), "directory_1", os.path.basename(str(self.ruta)), "dir_2:",
                      os.path.basename(os.path.dirname(os.path.normpath(str(self.ruta)))))
                audioTag = FLAC(str(fichero))
                audioTag['title'] = name_cancion
                audioTag['album'] = directorio
                audioTag['artist'] = parDir
                # Ni idea de como poner el album artist
                audioTag.save()
            except ID3NoHeaderError:
                audioTag = mutagen.File(fichero, easy=True)
                audioTag.add_tags()
                print("No existe un tag previo")

    def add_tag_m4a(self, fichero, name_cancion, parDir, directorio):  # No Funciona
        patronMusicam4a = re.compile('.\.m4a')
        if patronMusicam4a.search(str(fichero)):
            name_cancion = name_cancion.rstrip(".m4a")   # ahora al nombre le quitamos la extension que queda fea.
            try:
                print("file", os.path.basename(str(fichero)), "directory_1", os.path.basename(str(self.ruta)), "dir_2:",
                      os.path.basename(os.path.dirname(os.path.normpath(str(self.ruta)))))
                EasyMP4Tags.RegisterTextKey("artist", "@ART")
                audioTag = EasyMP4(str(fichero))
                audioTag['title'] = name_cancion
                audioTag['artist'] = parDir
                audioTag['album'] = directorio
                EasyMP4.RegisterTextKey("album_artist", "TPE2")
                audioTag['album_artist'] = ""
                print(audioTag['title'], "nuevo")
                audioTag.save()
            except:
                audioTag = mutagen.File(fichero, easy=True)
                audioTag.add_tags()
                audioTag['title'] = name_cancion
                audioTag['album'] = directorio
                audioTag['artist'] = parDir
                print("No existe un tag previo")
                audioTag.save(v2_version=3)
                audioTag.save()


tageador = mp3Tag()
tageador.main()
