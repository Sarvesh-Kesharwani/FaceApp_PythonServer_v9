i = 1;


                    //reciving photos
                    Log.d("receve", "Waiting for photo...");
                    ServerCardList.clear();
                    DataInputStream dis = new DataInputStream(sin);

                    i = 1;
                    int NoOfByteRead;
                     {//while (i <= NoOfPeople)
                        //receving one photo file
                        Log.d("receve", "Making PhotoBuffer.");
                        PersonPhotoBytes = new byte[PersonPhotoSizes.get(i - 1).intValue()];
                        Log.d("receve", "Buffer size to store this photo is:"+PersonPhotoSizes.get(i - 1).intValue());
                         NoOfByteRead = 0;

                         Log.d("receve", "Recieving Photo from Server in PhotoBuffer.");
                         dis.read(PersonPhotoBytes, 0, PersonPhotoBytes.length);
                         Log.d("receve", "NoOfBytesRead for one photo are: "+NoOfByteRead);

                       /* byte[] PhotoBuffer = new byte[1024];
                        while(NoOfByteRead < PersonPhotoBytes.length)
                        {
                            Log.d("receve", "lopp started...........");
                            Log.d("receve", "NoOfByteRead: "+NoOfByteRead);
                            Log.d("receve", "Left Bytes to read is: "+(PersonPhotoBytes.length-NoOfByteRead));

                            NoOfByteRead += dis.read(PhotoBuffer, 0, Math.min(PhotoBuffer.length, PersonPhotoBytes.length-NoOfByteRead));
                            Log.d("receve", "NoOfBytesRead for one photo are: "+NoOfByteRead);

                            Log.d("receve", "Copying to PersonPhotoBytes.-----------------------------------");
                            System.arraycopy(PhotoBuffer, 0, PersonPhotoBytes, 0, PhotoBuffer.length);
                        }*/
                        //Log.d("receve", "NoOfTotalBytesRead for one photo are: "+NoOfByteRead);

                        //offset+=PersonPhotoBytes.length-1;
                        Log.d("receve", "Photo Storing in ServerCardList............");
                        ServerCardList.add(new CardData(PersonPhotoBytes, PersonNames.get(i - 1), true, 1));

                        //making file directory
                        Log.d("receve", "Checking Directory...");
                        /*File myDir = new File(Permissions.,);//Environment.getExternalStorageDirectory() + "/DCIM" //Environment.getExternalStorageDirectory() + "/DCIM"
                        if (!myDir.exists()) {
                            Log.d("receve", "Directory not found!");
                            Log.d("receve", "Making Directory...");
                            myDir.mkdirs();
                        }
                        Log.d("receve", "Directory is already existing.");
                        */
                        //making file name
                        Log.d("receve", "Making FileName.");
                        String fileName = String.valueOf(PersonNames.get(i - 1)) + ".png";
                        Log.d("receve", "File Name is: " + fileName);

                        try { //making file with fileDir & fileName
                            Log.d("receve", "Making File at Directory...");
                            File imageFile = new File(Environment.getExternalStorageDirectory(), "/"+fileName);
                            if (imageFile == null) {
                                Log.d("receve", "ImageFile is Null!");
                                break;
                            }
                            //putting file in fos
                            Log.d("receve", "Putting file in FOS.");
                            fileout = new FileOutputStream(imageFile);

                            //converting ReceivedPhotoBytes to bitmap
                            Log.d("receve", "Converting PhotoBytes to PhotoBitmap.");
                            //Bitmap PersonPhotoBitmap = BitmapFactory.decodeByteArray(PersonPhotoBytes, 0, PersonPhotoBytes.length);

                            Bitmap PersonPhotoBitmap = Bitmap.createBitmap(215,234,Bitmap.Config.ARGB_8888);
                            ByteBuffer buff = ByteBuffer.wrap(PersonPhotoBytes);
                            buff.rewind();
                            PersonPhotoBitmap.copyPixelsFromBuffer(buff);

                            //convert bitmap to file
                            Log.d("receve", "Compressing PhotoBitmap to File.");
                            PersonPhotoBitmap.compress(Bitmap.CompressFormat.PNG, 100, fileout);
                            fileout.flush();
                            Log.d("receve", "Image was wrote successfully.");
                        } catch (IOException e) {
                            e.printStackTrace();
                        }



                       if (i == NoOfPeople) {
                                dis.close();
                                skt.close();
                                Log.d("receve", "Connection Closed Successfully.");
                            }
                            Log.d("receve", "Iteration: " + i + " Completed.");
                            i++;
                    }
                    Log.d("receve", "Adding to LocalDB....");
                    AddServerData(ServerCardList, NoOfPeople);
                    Log.d("receve", "Adding to LocalDB Completed.");
                } catch (UnknownHostException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }